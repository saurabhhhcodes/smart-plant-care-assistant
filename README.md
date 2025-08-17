# 🌱 Smart Plant Care Assistant

A powerful AI-powered application that uses **computer vision** and **large language models** to analyze plant health and provide personalized care recommendations. Built with Python and Streamlit for a seamless user experience.

## 🚀 Features

### 📷 Camera-First Analysis
- **Real-time Camera Integration**: Analyze plants directly using your device's camera
- **Automatic Analysis**: Set custom intervals for continuous monitoring
- **Instant Feedback**: Get immediate health assessments and care recommendations

### 🤖 AI-Powered Insights
- **Plant Health Analysis**: Comprehensive health status with confidence scores
- **Species Identification**: Automatic plant type detection
- **Issue Detection**: Identify common plant problems
- **Personalized Care Advice**: Get tailored recommendations for your plants
- **Chat Interface**: Ask questions about plant care in natural language

### 🛠️ Technical Features
- **Local AI Processing**: Uses Ollama for privacy-focused local inference
- **Computer Vision**: Advanced image analysis with OpenCV
- **Streamlit UI**: Clean, responsive interface that works on any device
- **Asynchronous Processing**: Smooth user experience with background analysis

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.8+**
- **Streamlit** for the web interface
- **Ollama** for local LLM inference
- **OpenCV** for computer vision
- **LangChain** for AI agent orchestration
- **LangGraph** for workflow management

### Key Dependencies
- **Pillow** for image processing
- **NumPy** for numerical operations
- **python-dotenv** for environment management
- **requests** for API calls

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- Webcam (for camera analysis)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/saurabhhhcodes/smart-plant-care-assistant.git
   cd smart-plant-care-assistant
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Ollama models**
   ```bash
   ollama pull llama3
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

The application will be available at `http://localhost:8501`

## 🎯 Usage

### Camera Analysis (Recommended)
1. Click the "Toggle Camera" button to start your camera
2. Position your plant in the frame
3. The app will automatically analyze the plant at regular intervals
4. View real-time analysis results including health status and care recommendations

### Photo Upload (Alternative Method)
1. Switch to the "Upload Photo" tab
2. Click "Browse files" or drag and drop an image
3. Click "Analyze Plant" to process the image
4. View detailed analysis results

### Chat with the Plant Expert
1. Scroll down to the chat interface
2. Ask any plant care questions in natural language
3. Get AI-powered responses based on the latest plant analysis

### Understanding the Analysis
- **Health Status**: Overall plant health with confidence score
- **Plant Type**: Identified species with confidence level
- **Potential Issues**: Any detected problems
- **Care Recommendations**: Personalized advice for your plant
- **AI Advice**: Personalized care recommendations

## 🔧 API Endpoints

### POST /api/analyze
Analyze a plant image and get health recommendations.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Response:**
```json
{
  "analysis": {
    "health": "good",
    "watering": "adequate",
    "light": "sufficient",
    "issues": [],
    "confidence": 85,
    "analysis_data": {
      "green_percentage": 75.2,
      "yellow_percentage": 2.1,
      "brown_percentage": 1.5,
      "health_score": 85.0
    }
  },
  "ai_advice": {
    "summary": "Your plant appears to be in good condition...",
    "recommendations": [...],
    "watering_schedule": "Continue current schedule",
    "care_tips": [...]
  }
}
```

### GET /api/health
Health check endpoint.

### GET /api/plants
Get common plant care information.

## 🏗️ Project Structure

```
smart-plant-care-assistant/
├── src/                    # React frontend source
│   ├── services/          # API services
│   ├── App.tsx           # Main component
│   └── index.tsx         # App entry point
├── backend/               # Python Flask backend
│   ├── app.py            # Main Flask application
│   ├── requirements.txt  # Python dependencies
│   └── README.md        # Backend documentation
├── public/               # Static assets
├── package.json          # Frontend dependencies
└── README.md            # This file
```

## 🚀 Deployment

### Frontend (GitHub Pages)
```bash
# Build for production
npm run build

# Deploy to GitHub Pages
npm run deploy
```

### Backend (Production)
```bash
# Install gunicorn
pip install gunicorn

# Deploy with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔍 Analysis Features

### Computer Vision Analysis
- **Green Detection**: Healthy plant tissue analysis
- **Yellow Detection**: Stress, nutrient deficiency, overwatering
- **Brown Detection**: Disease, death, severe damage
- **Color Distribution**: Percentage analysis of plant colors

### Health Scoring Algorithm
- **Excellent**: 80%+ health score
- **Good**: 60-79% health score
- **Fair**: 40-59% health score
- **Poor**: <40% health score

### AI Recommendations
- Personalized watering schedules
- Light condition advice
- Care tips and best practices
- Issue-specific solutions
- Plant-specific care information

## 🎨 UI/UX Features

### Mobile Optimization
- Touch-friendly interface
- Camera integration
- Responsive design
- Progressive Web App capabilities

### Visual Design
- Plant-inspired color scheme
- Modern, clean interface
- Intuitive navigation
- Loading states and animations

## 🔮 Future Enhancements

### Planned Features
- [ ] Plant species identification
- [ ] Care history tracking
- [ ] Push notifications for care reminders
- [ ] Multiple language support
- [ ] Social sharing features
- [ ] Advanced disease detection
- [ ] Growth tracking over time

### AI Improvements
- [ ] Fine-tuned plant care models
- [ ] Disease prediction algorithms
- [ ] Seasonal care adjustments
- [ ] Machine learning model training

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- React community for the excellent framework
- Tailwind CSS for the beautiful styling system
- Plant care experts for validation and feedback

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**🌱 Keep your plants healthy and happy with AI-powered care! 🌱**

*Built with ❤️ by [Saurabh](https://github.com/saurabhhhcodes)*
