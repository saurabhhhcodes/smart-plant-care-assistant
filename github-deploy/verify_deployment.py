#!/usr/bin/env python3
"""
Final verification script to ensure all files are present for deployment
"""

import os

def verify_deployment():
    """Verify that all necessary files are present for deployment."""
    print("Smart Plant Care Assistant - Final Deployment Verification")
    print("=" * 60)
    
    # List of required files
    required_files = [
        "streamlit_app.py",
        "plant_agent.py",
        "plant_analysis.py",
        "requirements.txt",
        "README.md",
        "deploy.sh",
        "deploy.bat",
        "FINAL_DEPLOYMENT_SUMMARY.md",
        "test_deployment.py",
        "deploy_to_github.py",
        ".gitignore"
    ]
    
    # List of required directories
    required_dirs = [
        ".streamlit"
    ]
    
    print("Checking required files...")
    all_files_present = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  [PASS] {file}")
        else:
            print(f"  [FAIL] {file} (MISSING)")
            all_files_present = False
    
    print("\nChecking required directories...")
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  [PASS] {directory}")
        else:
            print(f"  [FAIL] {directory} (MISSING)")
            all_files_present = False
    
    # Check config file
    config_file = os.path.join(".streamlit", "config.toml")
    if os.path.exists(config_file):
        print(f"  [PASS] {config_file}")
    else:
        print(f"  [FAIL] {config_file} (MISSING)")
        all_files_present = False
    
    print("\n" + "=" * 60)
    if all_files_present:
        print("[SUCCESS] All required files are present for deployment.")
        print("\nNext steps:")
        print("1. Run deploy_to_github.py to deploy to your GitHub repository")
        print("2. Go to Streamlit Cloud to deploy the application")
        print("3. Select your LLM provider and enter your API key in the app")
        return True
    else:
        print("[FAILURE] Some required files are missing.")
        print("Please check the missing files and try again.")
        return False

if __name__ == "__main__":
    verify_deployment()