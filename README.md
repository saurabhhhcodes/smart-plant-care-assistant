# 🌱 Smart Plant Care Assistant

A full-stack web application that uses **computer vision** and **AI** to analyze plant health and provide personalized care recommendations. Built with React (frontend) and Python Flask (backend).

## 🚀 Live Demo

**🌐 Live Application**: https://saurabhhhcodes.github.io/smart-plant-care-assistant

## ✨ Features

### 📱 Frontend (React + TypeScript)
- **Mobile-First Design**: Optimized for smartphones and tablets
- **Camera Integration**: Real-time plant photo capture
- **Photo Upload**: Upload existing plant images
- **Responsive UI**: Beautiful, modern interface with Tailwind CSS
- **Progressive Web App**: Installable on mobile devices

### 🔬 Backend (Python Flask)
- **Computer Vision Analysis**: Real plant health detection using OpenCV
- **Color Analysis**: Green, yellow, and brown color detection
- **AI Recommendations**: Personalized care advice based on analysis
- **RESTful API**: Easy integration and extensibility
- **Plant Database**: Common plant care information

### 🤖 AI-Powered Analysis
- **Health Assessment**: Excellent/Good/Fair/Poor ratings
- **Watering Analysis**: Needs water/Adequate/Excessive
- **Light Assessment**: Sufficient/Insufficient/Excessive
- **Issue Detection**: Automatic problem identification
- **Confidence Scoring**: Analysis accuracy indicators

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Canvas API** for image processing

### Backend
- **Python 3.8+** with Flask
- **OpenCV** for computer vision
- **NumPy** for numerical analysis
- **Pillow** for image processing
- **Flask-CORS** for cross-origin requests

## 📦 Installation

### Prerequisites
- Node.js 16+
- Python 3.8+
- npm or yarn
- pip

### Frontend Setup
```bash
# Clone the repository
git clone https://github.com/saurabhhhcodes/smart-plant-care-assistant.git
cd smart-plant-care-assistant

# Install dependencies
npm install

# Start development server
npm start
```

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start Flask server
python app.py
```

The backend API will be available at `http://localhost:5000`

## 🎯 Usage

### Camera Analysis (Primary Method)
1. Open the app on your mobile device
2. Grant camera permissions when prompted
3. Position your plant in the camera frame
4. Tap "Capture & Analyze"
5. Wait for AI analysis and recommendations

### Photo Upload (Secondary Method)
1. Switch to the "Upload" tab
2. Select a photo from your gallery
3. Wait for analysis and AI recommendations

### Understanding Results
- **Health Status**: Overall plant condition
- **Watering**: Current watering needs
- **Light**: Light condition assessment
- **Issues**: Detected problems or concerns
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
