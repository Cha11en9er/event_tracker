#!/bin/bash

echo "Deploying Event Tracker application..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create an .env file with your database configuration."
    echo "You can use .env.example as a template."
    exit 1
fi

# Pull latest changes if this is a git repository
if [ -d ".git" ]; then
    echo "Pulling latest changes..."
    git pull
fi

echo "Make sure your standalone PostgreSQL database is accessible at the host specified in your .env file"
echo "Database Host: $(grep DB_HOST .env | cut -d '=' -f2)"

# Build and start the containers
echo "Building and starting containers..."
docker-compose down
docker-compose up -d --build

echo "Deployment completed successfully!"
echo "Your application should be accessible at http://your-server-ip"
echo "To view logs, run: docker-compose logs -f" 