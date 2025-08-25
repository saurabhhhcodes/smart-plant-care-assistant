#!/bin/bash

# Deployment script for Smart Plant Care Assistant
# This script uses GitHub CLI and Streamlit CLI to deploy the application

# Check if required tools are installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/"
    exit 1
fi

if ! command -v streamlit &> /dev/null; then
    echo "Streamlit CLI is not installed. Please install it with: pip install streamlit"
    exit 1
fi

# Set variables
REPO_NAME="smart-plant-care-assistant"
GITHUB_USERNAME="saurabhhhcodes"

echo "Deploying Smart Plant Care Assistant..."

# Create GitHub repository
echo "Creating GitHub repository..."
gh repo create $GITHUB_USERNAME/$REPO_NAME --public --clone

# Navigate to repository directory
cd $REPO_NAME

# Copy files to repository
echo "Copying files to repository..."
cp ../streamlit_app.py .
cp ../plant_analysis.py .
cp ../requirements.txt .
cp -r ../.streamlit .
cp ../.env.example .

# Add files to git
echo "Adding files to git..."
git add .
git commit -m "Initial commit - Smart Plant Care Assistant for Streamlit Cloud"
git push origin main

echo "Repository created and files pushed to GitHub."

echo "Next steps:"
echo "1. Go to https://streamlit.io/cloud"
echo "2. Sign in with your GitHub account"
echo "3. Click 'New app'"
echo "4. Select your repository: $GITHUB_USERNAME/$REPO_NAME"
echo "5. Set the main file path to 'streamlit_app.py'"
echo "6. Click 'Deploy!'"

echo "Deployment script completed!"