# 🌱 Plant Care Assistant - Python Backend

## Overview
Flask-based REST API for plant health analysis using computer vision and AI.

## Features
- **Computer Vision Analysis**: Real plant health detection using OpenCV
- **Color Analysis**: Green, yellow, and brown color detection
- **AI Recommendations**: Personalized care advice based on analysis
- **Plant Database**: Common plant care information
- **RESTful API**: Easy integration with frontend

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
cd backend
pip install -r requirements.txt
```

## Usage

### Start the server
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### POST /api/analyze
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

#### GET /api/health
Health check endpoint.

#### GET /api/plants
Get common plant care information.

## Analysis Features

### Color Analysis
- **Green Detection**: Healthy plant tissue
- **Yellow Detection**: Stress, nutrient deficiency, overwatering
- **Brown Detection**: Disease, death, severe damage

### Health Scoring
- **Excellent**: 80%+ health score
- **Good**: 60-79% health score
- **Fair**: 40-59% health score
- **Poor**: <40% health score

### Recommendations
- Personalized watering schedules
- Light condition advice
- Care tips and best practices
- Issue-specific solutions

## Development

### Project Structure
```
backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding New Features
1. Extend the `PlantAnalyzer` class for new analysis methods
2. Add new endpoints in `app.py`
3. Update the `AICareAdvisor` for new recommendation types

## Deployment

### Local Development
```bash
python app.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Environment Variables
- `FLASK_ENV`: Set to 'production' for production deployment
- `PORT`: Server port (default: 5000)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
