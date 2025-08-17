@echo off
echo 🌱 Smart Plant Care Assistant - Deployment Script
echo.

echo 📋 Checking if repository exists...
git ls-remote https://github.com/saurabhhhcodes/smart-plant-care-assistant.git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Repository not found!
    echo.
    echo 🚀 Please create the repository first:
    echo 1. Go to: https://github.com/new
    echo 2. Name: smart-plant-care-assistant
    echo 3. Make it Public
    echo 4. Click Create repository
    echo.
    pause
    exit /b 1
)

echo ✅ Repository found! Starting deployment...
echo.

echo 🔄 Pushing code to GitHub...
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ Failed to push code
    pause
    exit /b 1
)

echo ✅ Code pushed successfully!
echo.

echo 🚀 Deploying to GitHub Pages...
npm run deploy
if %errorlevel% neq 0 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo.
echo 🎉 SUCCESS! Your app is deployed!
echo.
echo 🌐 Your app will be available at:
echo https://saurabhhhcodes.github.io/smart-plant-care-assistant
echo.
echo 📱 Don't forget to enable GitHub Pages:
echo 1. Go to your repository on GitHub
echo 2. Settings → Pages
echo 3. Source: Deploy from a branch
echo 4. Branch: gh-pages
echo 5. Save
echo.
pause
