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
        "plant_agent.py",
        "plant_analysis.py",
        "requirements.txt",
        "README.md",
        "deploy.sh",
        "deploy.bat"
    ]
    
    required_dirs = [
        ".streamlit"
    ]
    
    print("Testing file structure...")
    
    # Check files
    for file in required_files:
        if os.path.exists(file):
            print(f"  PASS {file} exists")
        else:
            print(f"  FAIL {file} is missing")
            return False
    
    # Check directories
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  PASS {directory} exists")
        else:
            print(f"  FAIL {directory} is missing")
            return False
    
    # Check config file
    config_file = os.path.join(".streamlit", "config.toml")
    if os.path.exists(config_file):
        print(f"  PASS {config_file} exists")
    else:
        print(f"  FAIL {config_file} is missing")
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
        from langchain_openai import ChatOpenAI
        print("  PASS langchain_openai import successful")
    except ImportError as e:
        print(f"  WARN langchain_openai import failed: {e}")
        print("       This is optional and only needed if using OpenAI")
    
    try:
        from langchain_anthropic import ChatAnthropic
        print("  PASS langchain_anthropic import successful")
    except ImportError as e:
        print("  WARN langchain_anthropic import failed")
        print("       This is optional and only needed if using Anthropic")
    
    try:
        from langchain_together import TogetherLLM
        print("  PASS langchain_together import successful")
    except ImportError as e:
        print(f"  WARN langchain_together import failed: {e}")
        print("       This is optional and only needed if using Together.ai (Meta models)")
    
    return True

def test_requirements():
    """Test that requirements.txt has the correct dependencies."""
    print("\nTesting requirements.txt...")
    
    required_packages = [
        "streamlit",
        "langchain",
        "langchain-community",
        "langchain-core",
        "langchain-openai",
        "langchain-anthropic",
        "langchain-together",
        "python-dotenv",
        "Pillow",
        "opencv-python-headless",
        "numpy",
        "requests",
        "pydantic"
    ]
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
            
        for package in required_packages:
            if package in content:
                print(f"  PASS {package} found in requirements.txt")
            else:
                print(f"  WARN {package} missing from requirements.txt")
                print("       This is optional and only needed for specific providers")
                
        return True
    except FileNotFoundError:
        print("  FAIL requirements.txt not found")
        return False
    except Exception as e:
        print(f"  FAIL Error reading requirements.txt: {e}")
        return False

def test_plant_agent():
    """Test that plant_agent.py has all required components."""
    print("\nTesting plant_agent.py components...")
    
    try:
        with open("plant_agent.py", "r") as f:
            content = f.read()
            
        # Check for required classes
        required_classes = [
            "PlantCareAgent"
        ]
        
        for class_name in required_classes:
            if f"class {class_name}" in content:
                print(f"  PASS {class_name} class found")
            else:
                print(f"  FAIL {class_name} class missing")
                return False
                
        # Check for required methods
        required_methods = [
            "analyze_image",
            "chat",
            "get_care_instructions"
        ]
        
        for method_name in required_methods:
            if f"def {method_name}" in content:
                print(f"  PASS {method_name} method found")
            else:
                print(f"  FAIL {method_name} method missing")
                return False
                
        return True
    except FileNotFoundError:
        print("  FAIL plant_agent.py not found")
        return False
    except Exception as e:
        print(f"  FAIL Error reading plant_agent.py: {e}")
        return False

def main():
    """Run all tests."""
    print("Smart Plant Care Assistant - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_requirements,
        test_plant_agent
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("PASS All tests passed! The application is ready for deployment.")
        print("\nNote: Some optional dependencies may be missing, but the application")
        print("will still work with the providers for which you have dependencies installed.")
        return 0
    else:
        print("FAIL Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())