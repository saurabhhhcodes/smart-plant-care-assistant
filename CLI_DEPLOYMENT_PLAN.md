# CLI Deployment Plan for Smart Plant Care Assistant

This document outlines how to deploy the Smart Plant Care Assistant application using GitHub CLI and Streamlit CLI with your GitHub username "saurabhhhcodes".

## Prerequisites

1. Install GitHub CLI: https://cli.github.com/
2. Install Streamlit: `pip install streamlit`
3. Authenticate with GitHub CLI: `gh auth login`

## Deployment Steps

### Step 1: Prepare the Application Files

1. Create a new directory for the deployment:
   ```bash
   mkdir smart-plant-care-assistant-deploy
   cd smart-plant-care-assistant-deploy
   ```

2. Copy the deployment version files:
   ```bash
   cp ../smart-plant-care-assistant/app_deploy.py streamlit_app.py
   cp ../smart-plant-care-assistant/plant_analysis.py .
   cp ../smart-plant-care-assistant/requirements.txt .
   cp -r ../smart-plant-care-assistant/.streamlit .
   cp ../smart-plant-care-assistant/.env.example .
   ```

3. Update requirements.txt to only include necessary dependencies:
   ```txt
   streamlit>=1.32.0
   python-dotenv>=1.0.0
   Pillow>=10.0.0
   opencv-python-headless>=4.8.0.74
   numpy>=1.24.0
   requests>=2.31.0
   ```

### Step 2: Create GitHub Repository with GitHub CLI

1. Create a new repository:
   ```bash
   gh repo create saurabhhhcodes/smart-plant-care-assistant --public
   ```

2. Initialize git and push files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Smart Plant Care Assistant for Streamlit Cloud"
   git branch -M main
   git remote add origin https://github.com/saurabhhhcodes/smart-plant-care-assistant.git
   git push -u origin main
   ```

### Step 3: Deploy to Streamlit Cloud

Streamlit Cloud doesn't currently have a CLI for direct deployment, but you can:

1. Go to https://streamlit.io/cloud
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `saurabhhhcodes/smart-plant-care-assistant`
5. Set the main file path to `streamlit_app.py`
6. Click "Deploy!"

Alternatively, you can use GitHub Actions to automate deployment when you push to your repository.

## GitHub Actions Deployment (Optional)

To automate deployment, you can create a GitHub Actions workflow:

1. Create `.github/workflows/streamlit-deploy.yml`:
   ```yaml
   name: Deploy to Streamlit Cloud
   
   on:
     push:
       branches: [ main ]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - name: Deploy to Streamlit Cloud
           run: |
             echo "Deploying to Streamlit Cloud"
             echo "Visit https://streamlit.io/cloud to complete deployment"
   ```

## Testing the Deployment

After deployment:

1. Visit your application URL (usually `https://smart-plant-care-assistant.streamlit.app`)
2. Test all features:
   - Camera analysis
   - Photo upload
   - Chat interface
   - Care library

## Updating the Application

To update your deployed application:

1. Make changes to your local files
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```
3. The GitHub Actions workflow will trigger, or you can manually redeploy from Streamlit Cloud