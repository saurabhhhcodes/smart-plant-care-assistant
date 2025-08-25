#!/bin/bash

# Deployment script for Smart Plant Care Assistant
# This script helps deploy the application to Streamlit Cloud

echo "Smart Plant Care Assistant - Deployment Script"
echo "=============================================="

# Check if required tools are installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed."
    echo "Please install it from https://cli.github.com/"
    exit 1
fi

if ! command -v streamlit &> /dev/null; then
    echo "Streamlit CLI is not installed."
    echo "Please install it with: pip install streamlit"
    exit 1
fi

# Set variables
REPO_NAME="smart-plant-care-assistant"
GITHUB_USERNAME="saurabhhhcodes"

echo "Creating GitHub repository..."
gh repo create $GITHUB_USERNAME/$REPO_NAME --public --clone

# Navigate to repository directory
cd $REPO_NAME

echo "Repository created successfully!"

echo "Next steps:"
echo "1. Copy all files from this directory to the new repository"
echo "2. Commit and push the files:"
echo "   git add ."
echo "   git commit -m 'Initial commit - Smart Plant Care Assistant'"
echo "   git push origin main"
echo "3. Go to https://streamlit.io/cloud"
echo "4. Sign in with your GitHub account"
echo "5. Click 'New app'"
echo "6. Select your repository: $GITHUB_USERNAME/$REPO_NAME"
echo "7. Set the main file path to 'streamlit_app.py'"
echo "8. Click 'Deploy!'"

echo "Deployment script completed!"