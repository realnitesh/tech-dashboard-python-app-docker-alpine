# Tech Support Dashboard

A comprehensive, interactive dashboard application built with Dash for analyzing and visualizing tech support ticket data. This application provides real-time insights into support operations, agent performance, and issue trends.

## 🚀 Quick Installation Guide

### **For New Users (No Docker Experience)**
Use the automated installer script that handles everything for you:

```bash
# 1. Clone the repository
git clone https://github.com/realnitesh/tech-dashboard-python-app-docker-alpine.git
cd tech-dashboard-python-app-docker-alpine

# 2. Make the script executable (Linux/macOS)
chmod +x docker+dashboard_install.sh

# 3. Run the automated installer
./docker+dashboard_install.sh

# 4. Access your dashboard
# Open http://localhost:8050 in your browser
```

**What the automated script does:**
- ✅ Detects your operating system automatically
- ✅ Installs Docker if not present (Linux systems)
- ✅ Starts Docker services
- ✅ Pulls pre-built image from Docker Hub
- ✅ Runs the application on port 8050
- ✅ Zero Docker knowledge required!

---

### **For Docker Users (Experienced)**
Use the start script for quick Docker deployment:

```bash
# 1. Clone the repository
git clone https://github.com/realnitesh/tech-dashboard-python-app-docker-alpine.git
cd tech-dashboard-python-app-docker-alpine

# 2. Run the start script
./start.sh

# 3. Access your dashboard
# Open http://localhost:8050 in your browser
```

**What the start script does:**
- 🐳 Builds Docker image locally
- 🐳 Runs container in background
- 🐳 Maps port 8050 to host

---

## 🎯 Features

### **Core Functionality**
- **CSV Data Upload & Processing**: Drag-and-drop CSV file upload with automatic data parsing
- **Interactive Visualizations**: Multiple chart types including bar charts, pie charts, line graphs, and tables
- **Real-time Filtering**: Date range filtering and dynamic data updates
- **Responsive Design**: Modern, mobile-friendly interface

### **Analytics & Insights**
- **Ticket Status Overview**: Visual representation of ticket status distribution
- **Agent Performance Tracking**: Monitor agent workload and closed ticket counts
- **Issue Categorization**: Analyze tech issues by category and subcategory
- **Knowledge Gap Analysis**: Identify areas requiring additional training or documentation
- **Age Analysis**: Track ticket aging and identify high-priority items
- **Weekly Comparisons**: Compare performance metrics across different time periods
- **JIRA Integration**: Direct links to JIRA tickets for seamless workflow

### **Data Export & Reporting**
- **Filtered Data Downloads**: Export filtered datasets based on user selections
- **High-Age Ticket Reports**: Generate reports for tickets requiring immediate attention
- **JIRA Link Exports**: Export ticket information with direct JIRA links

### **Advanced Features**
- **Real-time Data Processing**: Automatic column type detection and conversion
- **Interactive Drill-down**: Click on charts to filter data tables
- **Date Range Filtering**: Focus on specific time periods
- **Data Validation**: Automatic CSV format validation and error handling
- **Performance Optimization**: Built-in caching for large datasets

## 🛠️ Tools & Technologies Used

### **Backend & Core**
- **Python 3.9**: Core programming language
- **Dash**: Web framework for building analytical web applications
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing and array operations

### **Frontend & Visualization**
- **Plotly**: Interactive charts and graphs
- **HTML/CSS**: User interface components
- **Custom CSS**: Tailored styling for professional appearance
- **JavaScript**: Interactive dashboard functionality

### **Data Processing & Analytics**
- **CSV Parser**: Automatic date parsing and data validation
- **Data Preprocessing**: Automatic column type detection and conversion
- **Real-time Calculations**: Dynamic metrics and aggregations
- **Statistical Analysis**: Built-in statistical functions for insights

### **Deployment & Infrastructure**
- **Docker**: Containerized deployment
- **Alpine Linux**: Lightweight container base
- **Port 8050**: Standard web application port
- **Automated Scripts**: Cross-platform installation and deployment

## 📋 Requirements & Prerequisites

### **Software Requirements**
- **Docker**: Version 20.10+ (automatically installed by script on Linux)
- **Git**: For cloning the repository
- **Modern Web Browser**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+

### **Data Requirements**
Your CSV files must include these columns:
- `created_at`: Ticket creation date (DD-MM-YYYY HH:MM format)
- `ticket_status`: Current status of the ticket
- `cf_tech_issue_category`: Primary issue category
- `cf_cf_tech_issue_category_sub-category`: Issue subcategory
- `last_agent_assignment`: Agent assignment information
- `cf_is_tech_issue`: Boolean flag for tech issues
- `cf_knowledge_gap`: Knowledge gap indicators
- `user_email`: User contact information
- `cf_jira_link`: JIRA ticket links
- `title`: Ticket title/description
- `ticket_id`: Unique ticket identifier

## 📊 Usage Guide

### **Getting Started**
1. **Upload Data**: Click the "Upload CSV" button and select your tech support ticket CSV file
2. **Set Date Range**: Use the date picker to filter data by specific time periods
3. **Explore Visualizations**: Click on charts to drill down into specific data subsets
4. **Export Data**: Use the download links to export filtered datasets

### **Interactive Features**
- **Click on Charts**: Click any chart element to filter the data table below
- **Date Filtering**: Adjust date ranges to focus on specific time periods
- **Real-time Updates**: All visualizations update automatically when filters change
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### **Data Export Options**
- **Filtered Data**: Export data based on current chart selections
- **High-Age Tickets**: Generate reports for tickets requiring immediate attention
- **JIRA Integration**: Export ticket information with direct JIRA links
- **CSV Format**: All exports are in standard CSV format for easy analysis

## 🔧 Configuration

### **Environment Variables**
- `DASH_DEBUG`: Set to `True` for development mode (default: `True`)
- `PYTHONUNBUFFERED`: Ensures Python output is not buffered (default: `1`)
- `DASH_HOST`: Host binding (default: `0.0.0.0`)
- `DASH_PORT`: Port number (default: `8050`)

### **Port Configuration**
- **Default Port**: 8050
- **Custom Port**: Modify the Dockerfile or docker run command to use a different port
- **Port Mapping**: `-p 8050:8050` maps container port to host port

## 🐳 Docker Commands Reference

### **Build & Run**
```bash
# Build image
docker build -t tech-dashboard .

# Run container
docker run -p 8050:8050 tech-dashboard

# Run in background
docker run -d -p 8050:8050 --name tech-dashboard tech-dashboard

# Use pre-built image
docker run -p 8050:8050 realnitesh/tech-dashboard-python-app-docker-alpine
```

### **Container Management**
```bash
# Stop container
docker stop tech-dashboard

# Start container
docker start tech-dashboard

# View logs
docker logs tech-dashboard

# Remove container
docker rm tech-dashboard

# View running containers
docker ps
```

### **System Commands**
```bash
# View Docker stats
docker stats

# Clean up unused resources
docker system prune

# View Docker info
docker info
```

## 📁 Project Structure

```
tech-dashboard-python-app-docker-alpine/
├── dashboard.py                    # Main application file (633 lines)
├── requirements.txt                # Python dependencies
├── Dockerfile                     # Docker configuration
├── start.sh                       # Quick Docker start script
├── docker+dashboard_install.sh    # Automated Docker installer & deployment script
├── assets/
│   └── custom.css                # Custom styling (150 lines)
├── venv/                         # Python virtual environment
├── .venv/                        # Alternative virtual environment
├── .dockerignore                 # Docker ignore file
├── .gitignore                    # Git ignore file
└── README.md                     # This documentation file
```

## 🚨 Troubleshooting

### **Installation Issues**

**Script Permission Denied (Linux/macOS):**
```bash
chmod +x docker+dashboard_install.sh
chmod +x start.sh
```

**Docker Not Starting (Linux):**
```bash
# Check Docker service status
sudo systemctl status docker

# Start Docker manually
sudo systemctl start docker
sudo systemctl enable docker
```

**Port Already in Use:**
```bash
# Check what's using port 8050
netstat -ano | findstr :8050  # Windows
lsof -i :8050                 # macOS/Linux

# Use different port
docker run -p 8051:8050 tech-dashboard
```

### **Application Issues**

**CSV Upload Problems:**
- Ensure your CSV file has the required columns
- Check that date formats match DD-MM-YYYY HH:MM
- Verify the file is not corrupted
- Maximum file size: 100MB recommended

**Performance Issues:**
- **Large Datasets**: For files with >100,000 rows, consider data sampling
- **Memory Usage**: Monitor container memory usage with `docker stats`
- **Caching**: The application includes built-in data caching for better performance

**Browser Compatibility:**
- Use modern browsers (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
- Enable JavaScript for interactive features
- Clear browser cache if visualizations don't load

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/realnitesh/tech-dashboard-python-app-docker-alpine.git
cd tech-dashboard-python-app-docker-alpine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python dashboard.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the code comments in `dashboard.py`
- Check Docker logs: `docker logs <container-name>`

## 🔄 Updates & Maintenance

### **Updating Dependencies**
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Rebuild Docker image
docker build -t tech-dashboard .
```

### **Backup & Recovery**
- **Data**: Export important datasets regularly
- **Configuration**: Backup your Docker images and configurations
- **Customizations**: Document any custom CSS or configuration changes

### **Version Updates**
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
./start.sh
```

---

**Built with ❤️ using Dash, Python, and Docker**

**Quick Start**: `./docker+dashboard_install.sh` for new users | `./start.sh` for Docker users
