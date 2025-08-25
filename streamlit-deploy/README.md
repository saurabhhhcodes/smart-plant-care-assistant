# Smart Plant Care Assistant - Streamlit Deployment

This directory contains the files needed to deploy the Smart Plant Care Assistant application to Streamlit Cloud using GitHub CLI and Streamlit CLI.

## Files in this directory

1. `streamlit_app.py` - Main Streamlit application (based on app_deploy.py)
2. `plant_analysis.py` - Plant analysis utilities
3. `requirements.txt` - Python dependencies for deployment
4. `.streamlit/config.toml` - Streamlit configuration
5. `.env.example` - Environment variables template

## Deployment using GitHub CLI and Streamlit CLI

### Prerequisites

1. Install GitHub CLI: https://cli.github.com/
2. Install Streamlit: `pip install streamlit`
3. Authenticate with GitHub CLI: `gh auth login`

### Deployment Steps

1. Create a new repository on GitHub:
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

3. Deploy to Streamlit Cloud:
   - Go to https://streamlit.io/cloud
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository: `saurabhhhcodes/smart-plant-care-assistant`
   - Set the main file path to `streamlit_app.py`
   - Click "Deploy!"

## Required Files Content

### streamlit_app.py

This file should contain the content from `smart-plant-care-assistant/app_deploy.py` which is the deployment version of the application.

### requirements.txt

```txt
streamlit>=1.32.0
python-dotenv>=1.0.0
Pillow>=10.0.0
opencv-python-headless>=4.8.0.74
numpy>=1.24.0
requests>=2.31.0
```

### plant_analysis.py

This file should contain the content from `smart-plant-care-assistant/plant_analysis.py`.

### .streamlit/config.toml

This file should contain the content from `smart-plant-care-assistant/.streamlit/config.toml`.

### .env.example

This file should contain the content from `smart-plant-care-assistant/.env.example`.

## Testing the Application Locally

Before deploying, you can test the application locally:

```bash
streamlit run streamlit_app.py
```

## Updating the Deployed Application

To update your deployed application:

1. Make changes to your local files
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```
3. Redeploy from Streamlit Cloud