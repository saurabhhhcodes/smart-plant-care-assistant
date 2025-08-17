# 🌱 Smart Plant Care Assistant

A mobile-first React application that uses computer vision and open-source AI to analyze plant health and provide personalized care recommendations.

## Features

### 📱 Mobile-First Design
- Optimized for mobile devices with responsive design
- Camera integration for direct plant analysis
- Touch-friendly interface with intuitive navigation
- Progressive Web App (PWA) ready

### 🔬 Plant Analysis
- **Primary**: Direct camera capture for instant analysis
- **Secondary**: Photo upload option for existing images
- Simulated OpenCV analysis for:
  - Color analysis (yellowing, browning detection)
  - Shape analysis (wilting, curling detection)
  - Texture analysis (spots, disease detection)
  - Soil moisture inference

### 🤖 Open Source AI Integration
- **Ollama Integration**: Connect to local open-source LLMs
- **Fallback System**: Works offline with intelligent fallback responses
- **Personalized Advice**: Context-aware plant care recommendations
- **Multiple Models**: Support for various open-source models

### 📊 Analysis Results
- Plant health status (Excellent/Good/Fair/Poor)
- Watering recommendations
- Light condition assessment
- Issue detection and alerts
- Confidence scoring

### 💡 AI-Powered Recommendations
- Personalized care advice
- Watering schedules
- Care tips and best practices
- Actionable recommendations

## Technology Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **AI**: Ollama (open-source LLM)
- **Image Processing**: Canvas API (simulated OpenCV)
- **Mobile**: Responsive design with camera API

## Installation

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Ollama (optional, for enhanced AI features)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-plant-care-assistant
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open in browser**
   - Navigate to `http://localhost:3000`
   - For mobile testing, use your device's IP address

### Optional: Ollama Setup

For enhanced AI features, install Ollama:

1. **Install Ollama**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Pull a model**
   ```bash
   ollama pull llama3.2
   # or any other model you prefer
   ```

3. **Start Ollama**
   ```bash
   ollama serve
   ```

## Usage

### Camera Analysis (Primary Method)
1. Open the app on your mobile device
2. Grant camera permissions when prompted
3. Position your plant in the camera frame
4. Tap "Capture & Analyze"
5. Wait for analysis and AI recommendations

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

## Architecture

### Services
- **PlantAnalysisService**: Handles image analysis (simulated OpenCV)
- **LLMService**: Manages open-source AI integration

### Components
- **App.tsx**: Main application component
- **Camera Integration**: Real-time camera capture
- **Analysis Display**: Results visualization
- **AI Recommendations**: Personalized advice

### Data Flow
1. Image Capture → Plant Analysis → AI Processing → Recommendations
2. Fallback system ensures app works without external dependencies

## Mobile Optimization

### Camera Features
- Back camera preference for better plant photos
- High-resolution capture (1920x1080)
- Real-time preview with positioning guides
- Automatic camera management

### Performance
- Optimized for mobile browsers
- Efficient image processing
- Responsive design for all screen sizes
- Touch-friendly interface elements

## Development

### Project Structure
```
src/
├── services/
│   ├── llmService.ts      # Open-source AI integration
│   └── plantAnalysisService.ts  # Image analysis
├── App.tsx               # Main component
├── index.css            # Tailwind styles
└── index.tsx           # App entry point
```

### Adding Real OpenCV
To integrate real OpenCV.js:

1. Install OpenCV.js
   ```bash
   npm install opencv-js
   ```

2. Update `plantAnalysisService.ts` with real analysis methods
3. Implement color analysis, edge detection, and texture analysis

### Adding More LLM Models
1. Update `llmService.ts` with new model configurations
2. Add model selection UI
3. Test with different open-source models

## Deployment

### Build for Production
```bash
npm run build
```

### Deploy Options
- **Netlify**: Drag and drop `build` folder
- **Vercel**: Connect GitHub repository
- **Firebase**: Use Firebase Hosting
- **GitHub Pages**: Deploy from GitHub Actions

### PWA Features
- Add service worker for offline functionality
- Implement app manifest for installability
- Enable push notifications for care reminders

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Future Enhancements

### Planned Features
- [ ] Real OpenCV.js integration
- [ ] Plant species identification
- [ ] Care history tracking
- [ ] Push notifications
- [ ] Offline mode improvements
- [ ] Multiple language support
- [ ] Social sharing features

### AI Improvements
- [ ] Fine-tuned plant care models
- [ ] Disease prediction
- [ ] Growth tracking
- [ ] Seasonal care adjustments

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**🌱 Keep your plants healthy and happy with AI-powered care!**
