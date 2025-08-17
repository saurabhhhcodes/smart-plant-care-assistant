# 🌱 Smart Plant Care Assistant (Streamlit Version)

A Streamlit web application that uses AI to analyze plant health and provide care recommendations.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/saurabhhhcodes/smart-plant-care-assistant.git
   cd smart-plant-care-assistant
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Running the Application

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`

## 🛠️ Features

- **Image Upload**: Upload photos of your plants for analysis
- **AI-Powered Analysis**: Get instant feedback on plant health
- **Care Recommendations**: Receive personalized care advice
- **Responsive Design**: Works on desktop and mobile devices

## 🌐 Deployment

### Deploy to Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and connect your GitHub repository
4. Select the branch and main file (`app.py`)
5. Add your `OPENAI_API_KEY` in the advanced settings
6. Click "Deploy!"

### Deploy with Docker

1. Build the Docker image:
   ```bash
   docker build -t smart-plant-care .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 -e OPENAI_API_KEY=your_api_key smart-plant-care
   ```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/)
- Icons by [Font Awesome](https://fontawesome.com/)
