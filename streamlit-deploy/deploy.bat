@echo off
REM Deployment script for Smart Plant Care Assistant
REM This script uses GitHub CLI and Streamlit CLI to deploy the application

REM Check if required tools are installed
where gh >nul 2>&1
if %errorlevel% neq 0 (
    echo GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/
    pause
    exit /b 1
)

where streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Streamlit CLI is not installed. Please install it with: pip install streamlit
    pause
    exit /b 1
)

REM Set variables
set REPO_NAME=smart-plant-care-assistant
set GITHUB_USERNAME=saurabhhhcodes

echo Deploying Smart Plant Care Assistant...

REM Create GitHub repository
echo Creating GitHub repository...
gh repo create %GITHUB_USERNAME%/%REPO_NAME% --public --clone

REM Navigate to repository directory
cd %REPO_NAME%

REM Copy files to repository
echo Copying files to repository...
copy ..\streamlit_app.py .
copy ..\plant_analysis.py .
copy ..\requirements.txt .
xcopy ..\.streamlit .\.streamlit\ /E /I
copy ..\.env.example .

REM Add files to git
echo Adding files to git...
git add .
git commit -m "Initial commit - Smart Plant Care Assistant for Streamlit Cloud"
git push origin main

echo Repository created and files pushed to GitHub.

echo Next steps:
echo 1. Go to https://streamlit.io/cloud
echo 2. Sign in with your GitHub account
echo 3. Click "New app"
echo 4. Select your repository: %GITHUB_USERNAME%/%REPO_NAME%
echo 5. Set the main file path to "streamlit_app.py"
echo 6. Click "Deploy!"

echo Deployment script completed!
pause