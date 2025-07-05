import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime, timedelta
import numpy as np
import base64

app = dash.Dash(__name__)
app.title = "Tech Support Dashboard"

def parse_agent_name(assignment):
    if pd.isna(assignment):
        return "Unassigned"
    for part in str(assignment).split("||"):
        if "Name:" in part:
            return part.split("Name:")[1].strip()
    return "Unassigned"

def preprocess(df):
    # Parse dates with dd-mm-yyyy format explicitly
    df['created_at'] = pd.to_datetime(df['created_at'], format='%d-%m-%Y %H:%M', errors='coerce')
    df['agent_name'] = df['last_agent_assignment'].apply(parse_agent_name)
    df['age_hours'] = (pd.Timestamp.now() - df['created_at']).dt.total_seconds() / 3600
    # Ensure columns are pandas Series for correct method access
    for col in [
        'created_at', 'ticket_status', 'cf_tech_issue_category', 'cf_cf_tech_issue_category_sub-category',
        'agent_name', 'cf_is_tech_issue', 'cf_knowledge_gap', 'user_email', 'cf_jira_link', 'title', 'ticket_id', 'age_hours']:
        if col in df and isinstance(df[col], np.ndarray):
            df[col] = pd.Series(df[col])
    return df

app.layout = html.Div([
    html.H2("Tech Support Dashboard"),
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload CSV', style={'marginBottom': '20px'}),
        multiple=False
    ),
    html.Div(id='file-info'),
    html.Div(id='dashboard-content')
], style={'maxWidth': '1200px', 'margin': 'auto', 'padding': '20px'})

@app.callback(
    Output('dashboard-content', 'children'),
    Output('file-info', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_dashboard(contents, filename):
    if contents is None:
        return html.Div("Please upload a CSV file."), ""
    content_type, content_string = contents.split(',')
    decoded = io.BytesIO(base64.b64decode(content_string))
    df = pd.read_csv(decoded)
    df = preprocess(df)
    # Ensure 'created_at' is datetime with dd-mm-yyyy format
    df['created_at'] = pd.to_datetime(df['created_at'], format='%d-%m-%Y %H:%M', errors='coerce')
    created_at_min = df['created_at'].min()
    created_at_max = df['created_at'].max()
    min_date_dt = created_at_min if isinstance(created_at_min, (pd.Timestamp, datetime)) else None
    max_date_dt = created_at_max if isinstance(created_at_max, (pd.Timestamp, datetime)) else None

    # Date range filter
    date_picker = dcc.DatePickerRange(
        id='date-range',
        min_date_allowed=min_date_dt,
        max_date_allowed=max_date_dt,
        start_date=min_date_dt,
        end_date=max_date_dt,
        display_format='DD-MM-YYYY'
    )

    return [
        html.Div([
            html.Label("Filter by Date Range:"),
            date_picker
        ], style={'marginBottom': '20px'}),
        html.Div(id='visualizations', children=[]),
        dcc.Store(id='stored-data', data=df.to_json(date_format='iso', orient='split'))
    ], html.Div(f"Loaded file: {filename}")

@app.callback(
    Output('download-info', 'children'),
    Output('download-link', 'children'),
    Output('filtered-table', 'children'),
    Input('tickets-by-date-graph', 'clickData'),
    Input('status-pie-graph', 'clickData'),
    Input('top-categories-graph', 'clickData'),
    Input('top-subcategories-graph', 'clickData'),
    Input('agent-closed-graph', 'clickData'),
    Input('tech-issue-graph', 'clickData'),
    Input('knowledge-gap-graph', 'clickData'),
    Input('week-comparison-graph', 'clickData'),
    Input('last4-weeks-graph', 'clickData'),
    Input('jira-week-status-graph', 'clickData'),
    Input('stored-data', 'data')
)
def handle_graph_click(tickets_click, status_click, categories_click, subcategories_click, 
                      agent_click, tech_click, knowledge_click, week_click, last4_click, 
                      jira_click, data):
    if data is None:
        return "No data available", "", ""
    
    ctx = callback_context
    if not ctx.triggered:
        return "Click on any graph element to view and download filtered data", "", ""
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    click_data = ctx.triggered[0]['value']
    
    if not click_data:
        return "Click on any graph element to view and download filtered data", "", ""
    
    df = pd.read_json(data, orient='split')
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    df = pd.DataFrame(df.reset_index(drop=True))
    
    filtered_df = None
    filter_description = ""
    
    if triggered_id == 'status-pie-graph':
        # Extract status from the clicked pie slice
        point = click_data['points'][0]
        status_label = point['label']
        # Remove count from label (e.g., "Closed (150)" -> "Closed")
        status = status_label.split(' (')[0]
        filtered_df = df[df['ticket_status'] == status]
        filter_description = f"Tickets with status: {status}"
    
    elif triggered_id == 'top-categories-graph':
        # Extract category from the clicked bar
        point = click_data['points'][0]
        category_label = point['x']
        # Remove count from label
        category = category_label.split(' (')[0]
        filtered_df = df[df['cf_tech_issue_category'] == category]
        filter_description = f"Tickets with category: {category}"
    
    elif triggered_id == 'top-subcategories-graph':
        # Extract subcategory from the clicked bar
        point = click_data['points'][0]
        subcategory_label = point['x']
        # Remove count from label
        subcategory = subcategory_label.split(' (')[0]
        filtered_df = df[df['cf_cf_tech_issue_category_sub-category'] == subcategory]
        filter_description = f"Tickets with subcategory: {subcategory}"
    
    elif triggered_id == 'agent-closed-graph':
        # Extract agent from the clicked bar
        point = click_data['points'][0]
        agent = point['x']
        filtered_df = df[df['agent_name'] == agent]
        filter_description = f"Tickets assigned to agent: {agent}"
    
    elif triggered_id == 'tech-issue-graph':
        # Extract tech issue value from the clicked pie slice
        point = click_data['points'][0]
        tech_label = point['label']
        # Remove count from label
        tech_value = tech_label.split(' (')[0]
        filtered_df = df[df['cf_is_tech_issue'] == tech_value]
        filter_description = f"Tickets with tech issue: {tech_value}"
    
    elif triggered_id == 'knowledge-gap-graph':
        # Extract knowledge gap value from the clicked pie slice
        point = click_data['points'][0]
        knowledge_label = point['label']
        # Remove count from label
        knowledge_value = knowledge_label.split(' (')[0]
        filtered_df = df[df['cf_knowledge_gap'] == knowledge_value]
        filter_description = f"Tickets with knowledge gap: {knowledge_value}"
    
    elif triggered_id == 'tickets-by-date-graph':
        # Extract date and status from the clicked line point
        point = click_data['points'][0]
        date = point['x']
        status_label = point['customdata'][0] if 'customdata' in point else point['legendgroup']
        # Remove count from status label
        status = status_label.split(' (')[0]
        # Convert date string to datetime for filtering
        date_dt = pd.to_datetime(date, format='%d-%m-%Y')
        filtered_df = df[
            (df['created_at'].dt.date == date_dt.date()) & 
            (df['ticket_status'] == status)
        ]
        filter_description = f"Tickets created on {date} with status: {status}"
    
    elif triggered_id == 'week-comparison-graph':
        # Extract week from the clicked line point
        point = click_data['points'][0]
        week_label = point['x']
        year = point['customdata'][0] if 'customdata' in point else point['legendgroup']
        # Convert week label to date range
        week_start = pd.to_datetime(week_label, format='%d-%m-%Y')
        week_end = week_start + timedelta(days=6)
        filtered_df = df[
            (df['created_at'] >= week_start) & 
            (df['created_at'] <= week_end)
        ]
        filter_description = f"Tickets created in week starting {week_label}"
    
    elif triggered_id == 'last4-weeks-graph':
        # Extract week from the clicked bar
        point = click_data['points'][0]
        week_label = point['x']
        # Convert week label to date range
        week_start = pd.to_datetime(week_label, format='%d-%m-%Y')
        week_end = week_start + timedelta(days=6)
        filtered_df = df[
            (df['created_at'] >= week_start) & 
            (df['created_at'] <= week_end)
        ]
        filter_description = f"Tickets created in week starting {week_label}"
    
    elif triggered_id == 'jira-week-status-graph':
        # Extract week and status from the clicked bar
        point = click_data['points'][0]
        week_label = point['x']
        status_label = point['customdata'][0] if 'customdata' in point else point['legendgroup']
        # Remove count from status label
        status = status_label.split(' (')[0]
        # Convert week label to date range
        week_start = pd.to_datetime(week_label, format='%d-%m-%Y')
        week_end = week_start + timedelta(days=6)
        filtered_df = df[
            (df['created_at'] >= week_start) & 
            (df['created_at'] <= week_end) &
            (df['cf_jira_link'].notnull()) &
            (df['cf_jira_link'].astype(str).str.strip() != '')
        ]
        if status.lower() != 'total':
            filtered_df = filtered_df[filtered_df['ticket_status'].str.lower() == status.lower()]
        filter_description = f"Jira tickets in week starting {week_label} with status: {status}"
    
    if filtered_df is not None and len(filtered_df) > 0:
        filtered_df = pd.DataFrame(filtered_df.reset_index(drop=True))
        csv_string = filtered_df.to_csv(index=False)
        csv_bytes = csv_string.encode('utf-8')
        csv_b64 = base64.b64encode(csv_bytes).decode()
        download_link = html.A(
            f"Download {len(filtered_df)} records as CSV",
            id='download-csv',
            href=f'data:text/csv;base64,{csv_b64}',
            download=f'filtered_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            target='_blank',
            style={
                'display': 'inline-block',
                'margin': '10px',
                'padding': '10px 20px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'textDecoration': 'none',
                'borderRadius': '5px'
            }
        )
        # Show up to 100 rows in the table
        table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in filtered_df.columns],
            data=filtered_df.head(100).to_dict('records'),
            style_table={"overflowX": "auto", "overflowY": "auto", "maxHeight": "600px"},
            style_cell={"textAlign": "left", "maxWidth": 250, "whiteSpace": "normal"}
        )
        return f"Filter: {filter_description} - Found {len(filtered_df)} records", download_link, table
    
    return "No data found for the selected filter", "", ""

@app.callback(
    Output('visualizations', 'children'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('stored-data', 'data')
)
def update_visuals(start_date, end_date, data):
    if data is None:
        return []
    df = pd.read_json(data, orient='split')
    # Ensure df is a DataFrame (not ndarray)
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    # Handle date filtering with proper format conversion
    if start_date:
        start_dt = pd.to_datetime(start_date)
    else:
        start_dt = df['created_at'].min()
    
    if end_date:
        end_dt = pd.to_datetime(end_date)
    else:
        end_dt = df['created_at'].max()
    
    mask = (df['created_at'] >= start_dt) & (df['created_at'] <= end_dt)
    df = df[mask]
    df = pd.DataFrame(df.reset_index(drop=True))

    # 1. Total Created Tickets by Date
    tickets_by_date_status = df.groupby([df['created_at'].dt.date, 'ticket_status']).size().reset_index(name='Tickets')
    tickets_by_date_status = tickets_by_date_status.rename(columns={'created_at': 'date'})
    # Format date as dd-mm-yyyy for display and sort in ascending order
    tickets_by_date_status['date_formatted'] = pd.to_datetime(tickets_by_date_status['date']).dt.strftime('%d-%m-%Y')
    tickets_by_date_status = tickets_by_date_status.sort_values('date')

    # Calculate total count per status
    status_counts = tickets_by_date_status.groupby('ticket_status')['Tickets'].sum().to_dict()

    # Create a new column for legend labels with counts
    tickets_by_date_status['status_label'] = tickets_by_date_status['ticket_status'].apply(
        lambda s: f"{s} ({status_counts.get(s, 0)})"
    )

    fig_tickets_by_date = px.line(
        tickets_by_date_status,
        x='date_formatted',
        y='Tickets',
        color='status_label',
        title='Total Created Tickets by Date (Status-wise, with Counts)'
    )
    fig_tickets_by_date.update_layout(clickmode='event+select')

    # 2. Open vs Closed Status
    # Calculate counts for each status
    status_counts = df['ticket_status'].value_counts()
    status_label_map = {status: f"{status} ({count})" for status, count in status_counts.items()}
    df['ticket_status_label'] = df['ticket_status'].map(status_label_map)

    fig_status = px.pie(df, names='ticket_status_label', title='Open vs Closed Status (with Counts)')
    fig_status.update_layout(clickmode='event+select')

    # 3. Top Categories
    top_cats = df['cf_tech_issue_category'].value_counts().nlargest(10).reset_index()
    top_cats.columns = ['Category', 'Count']
    # Add count to category label for legend
    top_cats['CategoryLabel'] = top_cats.apply(lambda row: f"{row['Category']} ({row['Count']})", axis=1)
    fig_top_cats = px.bar(top_cats, x='CategoryLabel', y='Count', color='CategoryLabel', title='Top Tech Issue Categories (with Counts)')
    fig_top_cats.update_layout(clickmode='event+select')

    # Top Tech Sub-Categories
    top_subcats = df['cf_cf_tech_issue_category_sub-category'].value_counts().nlargest(10).reset_index()
    top_subcats.columns = ['Sub-Category', 'Count']
    # Add count to sub-category label for legend
    top_subcats['SubCategoryLabel'] = top_subcats.apply(lambda row: f"{row['Sub-Category']} ({row['Count']})", axis=1)
    fig_top_subcats = px.bar(top_subcats, x='SubCategoryLabel', y='Count', color='SubCategoryLabel', title='Top Tech Sub-Categories (with Counts)')
    fig_top_subcats.update_layout(clickmode='event+select')

    # 4. Agent Closed Tickets
    closed = df[df['ticket_status'].str.lower().str.contains('closed|resolved')]
    agent_closed = closed['agent_name'].value_counts().nlargest(10).reset_index()
    agent_closed.columns = ['Agent', 'Closed Tickets']
    fig_agent_closed = px.bar(agent_closed, x='Agent', y='Closed Tickets', title='Agent Closed Tickets')
    fig_agent_closed.update_layout(clickmode='event+select')

    # 5. Tech Issue Count
    # Calculate counts for each tech issue value
    tech_issue_counts = df['cf_is_tech_issue'].value_counts()
    tech_issue_label_map = {val: f"{val} ({count})" for val, count in tech_issue_counts.items()}
    df['cf_is_tech_issue_label'] = df['cf_is_tech_issue'].map(tech_issue_label_map)

    fig_tech_issue = px.pie(df, names='cf_is_tech_issue_label', title='Tech Issue (Yes/No) Count (with Counts)')
    fig_tech_issue.update_layout(clickmode='event+select')

    # 6. Knowledge Gap Count
    # Calculate counts for each knowledge gap value
    knowledge_gap_counts = df['cf_knowledge_gap'].value_counts()
    knowledge_gap_label_map = {val: f"{val} ({count})" for val, count in knowledge_gap_counts.items()}
    df['cf_knowledge_gap_label'] = df['cf_knowledge_gap'].map(knowledge_gap_label_map)

    fig_knowledge_gap = px.pie(df, names='cf_knowledge_gap_label', title='Knowledge Gap (Yes/No) Count (with Counts)')
    fig_knowledge_gap.update_layout(clickmode='event+select')

    # 7. Week-over-Week Comparison
    df['year'] = df['created_at'].dt.isocalendar().year
    df['week'] = df['created_at'].dt.isocalendar().week
    week_counts = df.groupby(['year', 'week']).size().reset_index(name='Tickets')
    # Create proper week labels with start date in dd-mm-yyyy format
    week_counts['week_start_date'] = pd.to_datetime(
        week_counts['year'].astype(str) + '-W' + week_counts['week'].astype(str).str.zfill(2) + '-1', 
        format='%Y-W%W-%w'
    )
    week_counts['week_label'] = week_counts['week_start_date'].dt.strftime('%d-%m-%Y')
    week_counts = week_counts.sort_values('week_start_date')
    fig_week = px.line(week_counts, x='week_label', y='Tickets', color='year', title='Week-over-Week Ticket Creation')
    fig_week.update_layout(clickmode='event+select')

    # 7b. Last 4 Weeks Comparison
    last_4_weeks = week_counts.sort_values('week_start_date', ascending=False).head(4).sort_values('week_start_date')
    last_4_weeks['label'] = last_4_weeks['week_label']
    fig_last4 = px.bar(last_4_weeks, x='label', y='Tickets', title='Ticket Counts: Last 4 Weeks')
    fig_last4.update_layout(clickmode='event+select')

    # 8. High Ageing Tickets
    high_age = df[(df['ticket_status'].str.lower() == 'open') & (df['age_hours'] > 72)]
    high_age = high_age.sort_values('age_hours', ascending=False)
    high_age_table = dash_table.DataTable(
        columns=[
            {'name': 'ticket_id', 'id': 'ticket_id'},
            {'name': 'title', 'id': 'title'},
            {'name': 'agent_name', 'id': 'agent_name'},
            {'name': 'age_hours', 'id': 'age_hours'}
        ],
        data=high_age[['ticket_id', 'title', 'agent_name', 'age_hours']].to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        page_size=10
    )

    # 9. Top Customers by Ticket Count (by email)
    top_customers = df['user_email'].value_counts().nlargest(10).reset_index()
    top_customers.columns = ['Email', 'Ticket Count']
    top_customers_table = dash_table.DataTable(
        columns=[{'name': i, 'id': i} for i in top_customers.columns],
        data=top_customers.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        page_size=10
    )

    # 10. Tickets with Jira Link and status open/onhold
    jira_tickets = df[
        df['cf_jira_link'].notnull() &
        (df['cf_jira_link'].astype(str).str.strip() != '') &
        (df['ticket_status'].str.lower().isin(['open', 'onhold']))
    ].copy()
    jira_tickets['age_days'] = (jira_tickets['age_hours'] // 24).astype(int)
    jira_tickets = jira_tickets.sort_values('age_days', ascending=False)
    jira_table = dash_table.DataTable(
        columns=[
            {'name': 'ticket_id', 'id': 'ticket_id'},
            {'name': 'ticket_status', 'id': 'ticket_status'},
            {'name': 'cf_jira_link', 'id': 'cf_jira_link'},
            {'name': 'age_days', 'id': 'age_days'}
        ],
        data=jira_tickets[['ticket_id', 'ticket_status', 'cf_jira_link', 'age_days']].to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        page_size=10
    )

    # Jira tickets with week-wise status breakdown (open, onhold, closed)
    jira_status = df[
        df['cf_jira_link'].notnull() & (df['cf_jira_link'].astype(str).str.strip() != '')
    ].copy()
    jira_status['status_group'] = jira_status['ticket_status'].str.lower().replace({
        'on hold': 'onhold', 'onhold': 'onhold', 'open': 'open', 'closed': 'closed', 'resolved': 'closed'
    })
    jira_status = jira_status[jira_status['status_group'].isin(['open', 'onhold', 'closed'])]
    # Group by week for Jira tickets with proper date formatting
    jira_status['year'] = jira_status['created_at'].dt.isocalendar().year
    jira_status['week'] = jira_status['created_at'].dt.isocalendar().week
    jira_status['week_start_date'] = jira_status.apply(
        lambda row: pd.to_datetime(f"{row['year']}-W{row['week']:02d}-1", format='%Y-W%W-%w'), axis=1
    )
    jira_status['week_label'] = jira_status['week_start_date'].dt.strftime('%d-%m-%Y')

    # Group by week and status
    jira_week_status = jira_status.groupby(['week_label', 'status_group']).size().reset_index(name='Count')

    # Calculate total Jira tickets per week
    jira_week_total = jira_status.groupby('week_label').size().reset_index(name='Count')
    jira_week_total['status_group'] = 'total'

    # Combine for plotting and sort by date
    jira_week_status = pd.concat([jira_week_status, jira_week_total], ignore_index=True)
    # Sort by week_label to maintain chronological order
    jira_week_status = jira_week_status.sort_values('week_label')

    # Calculate total count per status_group
    jira_status_group_counts = jira_week_status.groupby('status_group')['Count'].sum().to_dict()

    # Add count to legend labels
    jira_week_status['status_label'] = jira_week_status['status_group'].apply(
        lambda s: f"{s.capitalize()} ({jira_status_group_counts.get(s, 0)})"
    )

    total_jira_count = len(jira_status)

    fig_jira_week_status = px.bar(
        jira_week_status,
        x='week_label',
        y='Count',
        color='status_label',
        barmode='group',
        title='Jira Tickets by Status (Week-wise, including Total)'
    )
    fig_jira_week_status.update_layout(clickmode='event+select')

    return [
        dcc.Tabs([
            dcc.Tab(label='Dashboard', children=[
                html.Div([
                    dcc.Graph(id='tickets-by-date-graph', figure=fig_tickets_by_date)
                ]),
                html.Div([
                    dcc.Graph(id='status-pie-graph', figure=fig_status)
                ]),
                html.Div([
                    dcc.Graph(id='top-categories-graph', figure=fig_top_cats)
                ]),
                html.Div([
                    dcc.Graph(id='top-subcategories-graph', figure=fig_top_subcats)
                ]),
                html.Div([
                    dcc.Graph(id='agent-closed-graph', figure=fig_agent_closed)
                ]),
                html.Div([
                    dcc.Graph(id='tech-issue-graph', figure=fig_tech_issue)
                ]),
                html.Div([
                    dcc.Graph(id='knowledge-gap-graph', figure=fig_knowledge_gap)
                ]),
                html.Div([
                    dcc.Graph(id='week-comparison-graph', figure=fig_week)
                ]),
                html.Div([
                    dcc.Graph(id='last4-weeks-graph', figure=fig_last4)
                ]),
                html.H4(f"Total Jira Tickets: {total_jira_count}"),
                html.Div([
                    dcc.Graph(id='jira-week-status-graph', figure=fig_jira_week_status)
                ])
            ]),
            dcc.Tab(label='Download Filtered Data', children=[
                html.Div(id='download-section', children=[
                    html.H4("Click on any graph element above to view and download filtered data"),
                    html.Div(id='download-info'),
                    html.Div(id='download-link'),
                    html.Div(id='filtered-table')
                ])
            ]),
            dcc.Tab(label='Insights', children=[
                html.H4("High Ageing Tickets (Open > 72 hours)"),
                high_age_table,
                html.H4("Top Customers by Ticket Count (Email ID)"),
                top_customers_table,
                html.H4("Tickets with Jira Link"),
                jira_table
            ])
        ])
    ]

if __name__ == '__main__':
    app.run(debug=True)



