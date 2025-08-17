@echo off
echo 🌱 Smart Plant Care Assistant - Full Stack Startup
echo.

echo 📋 Starting both frontend and backend...
echo.

echo 🔧 Starting Python Backend...
start "Backend" cmd /k "cd backend && python app.py"

echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo 🎨 Starting React Frontend...
start "Frontend" cmd /k "npm start"

echo.
echo 🎉 Both services are starting!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo.
echo 🌐 Live Demo: https://saurabhhhcodes.github.io/smart-plant-care-assistant
echo.
pause
