@echo off
REM Deployment script for Smart Plant Care Assistant
REM This script helps deploy the application to Streamlit Cloud

echo Smart Plant Care Assistant - Deployment Script
echo ==============================================

REM Check if required tools are installed
where gh >nul 2>&1
if %errorlevel% neq 0 (
    echo GitHub CLI (gh) is not installed.
    echo Please install it from https://cli.github.com/
    pause
    exit /b 1
)

where streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Streamlit CLI is not installed.
    echo Please install it with: pip install streamlit
    pause
    exit /b 1
)

REM Set variables
set REPO_NAME=smart-plant-care-assistant
set GITHUB_USERNAME=saurabhhhcodes

echo Creating GitHub repository...
gh repo create %GITHUB_USERNAME%/%REPO_NAME% --public --clone

echo Repository created successfully!

echo Next steps:
echo 1. Copy all files from this directory to the new repository
echo 2. Commit and push the files:
echo    git add .
echo    git commit -m "Initial commit - Smart Plant Care Assistant"
echo    git push origin main
echo 3. Go to https://streamlit.io/cloud
echo 4. Sign in with your GitHub account
echo 5. Click "New app"
echo 6. Select your repository: %GITHUB_USERNAME%/%REPO_NAME%
echo 7. Set the main file path to "streamlit_app.py"
echo 8. Click "Deploy!"

echo Deployment script completed!
pause