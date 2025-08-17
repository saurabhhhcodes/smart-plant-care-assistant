# Cleanup script for Smart Plant Care Assistant
# This script removes unnecessary files from the project

# Remove React frontend files
Remove-Item -Recurse -Force -Path "public" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force -Path "src" -ErrorAction SilentlyContinue
Remove-Item -Force "package.json" -ErrorAction SilentlyContinue
Remove-Item -Force "package-lock.json" -ErrorAction SilentlyContinue
Remove-Item -Force "tsconfig.json" -ErrorAction SilentlyContinue
Remove-Item -Force "tailwind.config.js" -ErrorAction SilentlyContinue
Remove-Item -Force "postcss.config.js" -ErrorAction SilentlyContinue
Remove-Item -Force "start.bat" -ErrorAction SilentlyContinue

# Remove backend files that are no longer needed
Remove-Item -Recurse -Force -Path "backend" -ErrorAction SilentlyContinue

# Remove deployment files that are no longer needed
Remove-Item -Force "Dockerfile" -ErrorAction SilentlyContinue
Remove-Item -Force "REPLIT_DEPLOYMENT.md" -ErrorAction SilentlyContinue

Write-Host "Cleanup completed. The following essential files remain:"
Get-ChildItem -File -Recurse | Select-Object FullName
