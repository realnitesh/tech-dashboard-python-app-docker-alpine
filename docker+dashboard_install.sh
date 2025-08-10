#!/bin/bash

set -e

echo "=== Tech Dashboard Auto-Installer ==="

# Detect OS
OS="$(uname -s)"

if [[ "$OS" == "Darwin" ]]; then
    echo "Detected MacOS."
    # Check if Docker is installed
    if ! command -v docker >/dev/null 2>&1; then
        echo "Docker is not installed. Please install Docker Desktop for Mac from https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
    # Start Docker Desktop if not running (user must do this manually)
    if ! docker info >/dev/null 2>&1; then
        echo "Docker Desktop does not appear to be running. Please start Docker Desktop and try again."
        exit 1
    fi
else
    echo "Detected Linux."
    # Check if Docker is installed
    if ! command -v docker >/dev/null 2>&1; then
        echo "Docker not found. Installing Docker..."
        # (Insert Ubuntu install steps here, as in previous script)
        # ... (see previous script for details)
    fi
    echo "Starting Docker service..."
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# Remove old container if exists
if docker ps -a --format '{{.Names}}' | grep -Eq '^tech_dashboard_app$'; then
    echo "Removing old tech_dashboard_app container..."
    docker rm -f tech_dashboard_app
fi

echo "Pulling and running the Dash app container..."
docker run -d --name tech_dashboard_app -p 8050:8050 realnitesh/tech_dashboard:latest

echo "=== All done! Open http://localhost:8050 in your browser. ==="
