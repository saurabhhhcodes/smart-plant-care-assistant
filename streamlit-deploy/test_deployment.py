#!/usr/bin/env python3
"""
Test script to verify that all components of the Smart Plant Care Assistant
are working correctly for deployment.
"""

import sys
import os
from pathlib import Path

def test_file_structure():
    """Test that all required files are present."""
    required_files = [
        "streamlit_app.py",
        "plant_analysis.py",
        "requirements.txt",
        ".env.example"
    ]
    
    required_dirs = [
        ".streamlit"
    ]
    
    print("Testing file structure...")
    
    # Check files
    for file in required_files:
        if os.path.exists(os.path.join("streamlit-deploy", file)):
            print(f"  PASS {file} exists")
        else:
            print(f"  FAIL {file} is missing")
            return False
    
    # Check directories
    for directory in required_dirs:
        if os.path.exists(os.path.join("streamlit-deploy", directory)):
            print(f"  PASS {directory} exists")
        else:
            print(f"  FAIL {directory} is missing")
            return False
    
    # Check config file
    config_file = os.path.join("streamlit-deploy", ".streamlit", "config.toml")
    if os.path.exists(config_file):
        print(f"  PASS config.toml exists")
    else:
        print(f"  FAIL config.toml is missing")
        return False
    
    return True

def test_imports():
    """Test that all required imports work."""
    print("\nTesting imports...")
    
    try:
        import streamlit as st
        print("  PASS streamlit import successful")
    except ImportError as e:
        print(f"  FAIL streamlit import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("  PASS PIL import successful")
    except ImportError as e:
        print(f"  FAIL PIL import failed: {e}")
        return False
    
    try:
        import cv2
        print("  PASS cv2 import successful")
    except ImportError as e:
        print(f"  FAIL cv2 import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("  PASS numpy import successful")
    except ImportError as e:
        print(f"  FAIL numpy import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  PASS dotenv import successful")
    except ImportError as e:
        print(f"  FAIL dotenv import failed: {e}")
        return False
    
    return True

def test_requirements():
    """Test that requirements.txt has the correct dependencies."""
    print("\nTesting requirements.txt...")
    
    required_packages = [
        "streamlit",
        "python-dotenv",
        "Pillow",
        "opencv-python-headless",
        "numpy",
        "requests"
    ]
    
    try:
        with open("streamlit-deploy/requirements.txt", "r") as f:
            content = f.read()
            
        for package in required_packages:
            if package in content:
                print(f"  PASS {package} found in requirements.txt")
            else:
                print(f"  FAIL {package} missing from requirements.txt")
                return False
                
        return True
    except FileNotFoundError:
        print("  FAIL requirements.txt not found")
        return False
    except Exception as e:
        print(f"  FAIL Error reading requirements.txt: {e}")
        return False

def test_streamlit_app():
    """Test that streamlit_app.py has all required components."""
    print("\nTesting streamlit_app.py components...")
    
    try:
        with open("streamlit-deploy/streamlit_app.py", "r") as f:
            content = f.read()
            
        # Check for required classes
        required_classes = [
            "MockPlantCareAgent",
            "SimplePlantAnalyzer"
        ]
        
        for class_name in required_classes:
            if f"class {class_name}" in content:
                print(f"  PASS {class_name} class found")
            else:
                print(f"  FAIL {class_name} class missing")
                return False
                
        # Check for required functions
        required_functions = [
            "display_camera_analysis",
            "display_upload_section",
            "display_chat_interface",
            "display_care_library"
        ]
        
        for function_name in required_functions:
            if f"def {function_name}" in content:
                print(f"  PASS {function_name} function found")
            else:
                print(f"  FAIL {function_name} function missing")
                return False
                
        return True
    except FileNotFoundError:
        print("  FAIL streamlit_app.py not found")
        return False
    except Exception as e:
        print(f"  FAIL Error reading streamlit_app.py: {e}")
        return False

def main():
    """Run all tests."""
    print("Smart Plant Care Assistant - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_requirements,
        test_streamlit_app
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("PASS All tests passed! The application is ready for deployment.")
        return 0
    else:
        print("FAIL Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())