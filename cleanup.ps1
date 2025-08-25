# Cleanup script for Smart Plant Care Assistant
# Removes unnecessary files before committing to GitHub

# Files to remove
$filesToRemove = @(
    "check_env.py",
    "check_python.bat",
    "setup_and_run.bat",
    "setup_and_run.ps1",
    "test_plant_care.py",
    "test_python.py"
)

# Folders to remove
$foldersToRemove = @(
    "__pycache__"
)

# Remove files
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "Removed file: $file"
    }
}

# Remove folders
foreach ($folder in $foldersToRemove) {
    if (Test-Path $folder) {
        Remove-Item $folder -Recurse -Force
        Write-Host "Removed folder: $folder"
    }
}

Write-Host "\nCleanup complete! The project is now ready for GitHub."
Write-Host "Run these commands to push to GitHub:"
Write-Host "1. git add ."
Write-Host "2. git commit -m 'Initial commit'"
Write-Host "3. git push origin main"
