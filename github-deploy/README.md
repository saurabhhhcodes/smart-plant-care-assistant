# Smart Plant Care Assistant

A Streamlit-based application that helps you take care of your plants using AI-powered image analysis and chat assistance with real LLMs.

## Features

- 📸 Upload plant images for health analysis
- 💬 Chat with an AI plant care assistant
- 🌿 Get personalized care recommendations
- 🔍 Identify plant health issues
- 🌐 Supports multiple LLM providers (OpenAI, Anthropic, Meta, etc.)

## Prerequisites

- Python 3.8+

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/saurabhhhcodes/smart-plant-care-assistant.git
   cd smart-plant-care-assistant
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys in the application (no need to set environment variables)

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Select your preferred LLM provider and enter your API key in the sidebar

## Supported LLM Providers

- OpenAI (GPT-3.5, GPT-4, etc.)
- Anthropic (Claude models)
- Meta (through Together.ai - Llama models)
- Other providers via Together.ai integration

## Deployed Version

This application is designed to work with Streamlit Cloud. Users can select their preferred LLM provider and enter their API key directly in the application interface.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.