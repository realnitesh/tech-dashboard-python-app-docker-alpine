
# Build image
docker build -t  tech_dashboard:latest .

# Run container
docker run -d -p 8050:8050 tech_dashboard:latest