import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px
import io
from datetime import datetime, timedelta
import numpy as np

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
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce', dayfirst=True)
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
    # Ensure 'created_at' is datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce', dayfirst=True)
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
        display_format='YYYY-MM-DD'
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
    mask = (df['created_at'] >= pd.to_datetime(start_date)) & (df['created_at'] <= pd.to_datetime(end_date))
    df = df[mask]
    df = pd.DataFrame(df.reset_index(drop=True))

    # 1. Total Created Tickets by Date
    tickets_by_date_status = df.groupby([df['created_at'].dt.date, 'ticket_status']).size().reset_index(name='Tickets')
    tickets_by_date_status = tickets_by_date_status.rename(columns={'created_at': 'date'})

    # Calculate total count per status
    status_counts = tickets_by_date_status.groupby('ticket_status')['Tickets'].sum().to_dict()

    # Create a new column for legend labels with counts
    tickets_by_date_status['status_label'] = tickets_by_date_status['ticket_status'].apply(
        lambda s: f"{s} ({status_counts.get(s, 0)})"
    )

    fig_tickets_by_date = px.line(
        tickets_by_date_status,
        x='date',
        y='Tickets',
        color='status_label',
        title='Total Created Tickets by Date (Status-wise, with Counts)'
    )

    # 2. Open vs Closed Status
    # Calculate counts for each status
    status_counts = df['ticket_status'].value_counts()
    status_label_map = {status: f"{status} ({count})" for status, count in status_counts.items()}
    df['ticket_status_label'] = df['ticket_status'].map(status_label_map)

    fig_status = px.pie(df, names='ticket_status_label', title='Open vs Closed Status (with Counts)')

    # 3. Top Categories
    top_cats = df['cf_tech_issue_category'].value_counts().nlargest(10).reset_index()
    top_cats.columns = ['Category', 'Count']
    # Add count to category label for legend
    top_cats['CategoryLabel'] = top_cats.apply(lambda row: f"{row['Category']} ({row['Count']})", axis=1)
    fig_top_cats = px.bar(top_cats, x='CategoryLabel', y='Count', color='CategoryLabel', title='Top Tech Issue Categories (with Counts)')

    # Top Tech Sub-Categories
    top_subcats = df['cf_cf_tech_issue_category_sub-category'].value_counts().nlargest(10).reset_index()
    top_subcats.columns = ['Sub-Category', 'Count']
    # Add count to sub-category label for legend
    top_subcats['SubCategoryLabel'] = top_subcats.apply(lambda row: f"{row['Sub-Category']} ({row['Count']})", axis=1)
    fig_top_subcats = px.bar(top_subcats, x='SubCategoryLabel', y='Count', color='SubCategoryLabel', title='Top Tech Sub-Categories (with Counts)')

    # 4. Agent Closed Tickets
    closed = df[df['ticket_status'].str.lower().str.contains('closed|resolved')]
    agent_closed = closed['agent_name'].value_counts().nlargest(10).reset_index()
    agent_closed.columns = ['Agent', 'Closed Tickets']
    fig_agent_closed = px.bar(agent_closed, x='Agent', y='Closed Tickets', title='Agent Closed Tickets')

    # 5. Tech Issue Count
    # Calculate counts for each tech issue value
    tech_issue_counts = df['cf_is_tech_issue'].value_counts()
    tech_issue_label_map = {val: f"{val} ({count})" for val, count in tech_issue_counts.items()}
    df['cf_is_tech_issue_label'] = df['cf_is_tech_issue'].map(tech_issue_label_map)

    fig_tech_issue = px.pie(df, names='cf_is_tech_issue_label', title='Tech Issue (Yes/No) Count (with Counts)')

    # 6. Knowledge Gap Count
    # Calculate counts for each knowledge gap value
    knowledge_gap_counts = df['cf_knowledge_gap'].value_counts()
    knowledge_gap_label_map = {val: f"{val} ({count})" for val, count in knowledge_gap_counts.items()}
    df['cf_knowledge_gap_label'] = df['cf_knowledge_gap'].map(knowledge_gap_label_map)

    fig_knowledge_gap = px.pie(df, names='cf_knowledge_gap_label', title='Knowledge Gap (Yes/No) Count (with Counts)')

    # 7. Week-over-Week Comparison
    df['year'] = df['created_at'].dt.isocalendar().year
    df['week'] = df['created_at'].dt.isocalendar().week
    week_counts = df.groupby(['year', 'week']).size().reset_index(name='Tickets')
    fig_week = px.line(week_counts, x='week', y='Tickets', color='year', title='Week-over-Week Ticket Creation')

    # 7b. Last 4 Weeks Comparison
    last_4_weeks = week_counts.sort_values(['year', 'week'], ascending=[False, False]).head(4).sort_values(['year', 'week'])
    last_4_weeks['label'] = last_4_weeks['year'].astype(str) + '-W' + last_4_weeks['week'].astype(str)
    fig_last4 = px.bar(last_4_weeks, x='label', y='Tickets', title='Ticket Counts: Last 4 Weeks')

    # 8. High Ageing Tickets
    high_age = df[(df['ticket_status'].str.lower() == 'open') & (df['age_hours'] > 72)]
    high_age = high_age.sort_values('age_hours', ascending=False)
    high_age_table = dash_table.DataTable(
        columns=[{'name': i, 'id': i} for i in ['ticket_id', 'title', 'age_hours']],
        data=high_age[['ticket_id', 'title', 'age_hours']].to_dict('records'),
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
    ]
    jira_table = dash_table.DataTable(
        columns=[{'name': i, 'id': i} for i in ['ticket_id', 'ticket_status', 'cf_jira_link']],
        data=jira_tickets[['ticket_id', 'ticket_status', 'cf_jira_link']].to_dict('records'),
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
    jira_status['week_label'] = jira_status['created_at'].dt.strftime('%Y-W%U')

    # Group by week and status
    jira_week_status = jira_status.groupby(['week_label', 'status_group']).size().reset_index(name='Count')

    # Calculate total Jira tickets per week
    jira_week_total = jira_status.groupby('week_label').size().reset_index(name='Count')
    jira_week_total['status_group'] = 'total'

    # Combine for plotting
    jira_week_status = pd.concat([jira_week_status, jira_week_total], ignore_index=True)

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

    return [
        dcc.Tabs([
            dcc.Tab(label='Dashboard', children=[
                html.Div([
                    dcc.Graph(figure=fig_tickets_by_date)
                ]),
                html.Div([
                    dcc.Graph(figure=fig_status)
                ]),
                html.Div([
                    dcc.Graph(figure=fig_top_cats)
                ]),
                html.Div([
                    dcc.Graph(figure=fig_top_subcats)
                ]),
                html.Div([
                    dcc.Graph(figure=fig_agent_closed)
                ]),
                html.Div([
                    dcc.Graph(figure=fig_tech_issue)
                ]),
                html.Div([
                    dcc.Graph(figure=fig_knowledge_gap)
                ]),
                html.Div([
                    dcc.Graph(figure=fig_week)
                ]),
                html.Div([
                    dcc.Graph(figure=fig_last4)
                ]),
                html.H4(f"Total Jira Tickets: {total_jira_count}"),
                html.Div([
                    dcc.Graph(figure=fig_jira_week_status)
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
    import base64
    app.run(debug=True)



