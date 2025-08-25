#!/usr/bin/env python3
"""
Script to help deploy the Smart Plant Care Assistant to GitHub
"""

import os
import subprocess
import sys

def check_prerequisites():
    """Check if required tools are installed."""
    print("Checking prerequisites...")
    
    # Check if git is installed
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print("  PASS Git is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  FAIL Git is not installed")
        print("       Please install Git from https://git-scm.com/")
        return False
    
    # Check if GitHub CLI is installed
    try:
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
        print("  PASS GitHub CLI is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  FAIL GitHub CLI is not installed")
        print("       Please install GitHub CLI from https://cli.github.com/")
        return False
    
    return True

def create_github_repo():
    """Create a new GitHub repository."""
    print("\nCreating GitHub repository...")
    
    repo_name = "smart-plant-care-assistant"
    username = "saurabhhhcodes"
    
    try:
        # Create the repository
        subprocess.run([
            "gh", "repo", "create", 
            f"{username}/{repo_name}", 
            "--public", 
            "--clone"
        ], check=True)
        print(f"  PASS Repository {username}/{repo_name} created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  FAIL Failed to create repository: {e}")
        return False

def deploy_files():
    """Deploy files to the GitHub repository."""
    print("\nDeploying files to GitHub...")
    
    try:
        # Change to the repository directory
        os.chdir("smart-plant-care-assistant")
        
        # Copy files from parent directory
        files_to_copy = [
            "streamlit_app.py",
            "plant_agent.py",
            "plant_analysis.py",
            "requirements.txt",
            "README.md",
            "deploy.sh",
            "deploy.bat",
            "FINAL_DEPLOYMENT_SUMMARY.md",
            "test_deployment.py"
        ]
        
        dirs_to_copy = [
            ".streamlit"
        ]
        
        # Copy files
        for file in files_to_copy:
            if os.path.exists(f"../{file}"):
                subprocess.run(["cp", f"../{file}", "."], check=True)
                print(f"  PASS Copied {file}")
            else:
                print(f"  WARN {file} not found")
        
        # Copy directories
        for directory in dirs_to_copy:
            if os.path.exists(f"../{directory}"):
                subprocess.run(["cp", "-r", f"../{directory}", "."], check=True)
                print(f"  PASS Copied {directory}")
            else:
                print(f"  WARN {directory} not found")
        
        # Add, commit, and push
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit - Smart Plant Care Assistant"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("  PASS Files deployed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  FAIL Failed to deploy files: {e}")
        return False
    except Exception as e:
        print(f"  FAIL Error: {e}")
        return False

def main():
    """Main function."""
    print("Smart Plant Care Assistant - GitHub Deployment Helper")
    print("=" * 55)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPlease install the required tools and try again.")
        return 1
    
    # Create GitHub repository
    if not create_github_repo():
        print("\nFailed to create GitHub repository.")
        return 1
    
    # Deploy files
    if not deploy_files():
        print("\nFailed to deploy files to GitHub.")
        return 1
    
    print("\n" + "=" * 55)
    print("SUCCESS! The application has been deployed to GitHub.")
    print("\nNext steps:")
    print("1. Go to https://streamlit.io/cloud")
    print("2. Sign in with your GitHub account")
    print("3. Click 'New app'")
    print("4. Select your repository: saurabhhhcodes/smart-plant-care-assistant")
    print("5. Set the main file path to 'streamlit_app.py'")
    print("6. Click 'Deploy!'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())