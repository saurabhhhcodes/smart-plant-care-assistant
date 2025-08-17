from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

class PlantAnalyzer:
    def __init__(self):
        self.health_thresholds = {
            'excellent': 0.8,
            'good': 0.6,
            'fair': 0.4,
            'poor': 0.2
        }
    
    def analyze_image(self, image_data):
        """Analyze plant image for health indicators"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            
            # Analyze green color (healthy plants)
            green_lower = np.array([35, 50, 50])
            green_upper = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            green_percentage = np.sum(green_mask > 0) / (green_mask.shape[0] * green_mask.shape[1])
            
            # Analyze yellow/brown colors (unhealthy indicators)
            yellow_lower = np.array([20, 100, 100])
            yellow_upper = np.array([30, 255, 255])
            yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            yellow_percentage = np.sum(yellow_mask > 0) / (yellow_mask.shape[0] * yellow_mask.shape[1])
            
            # Analyze brown colors (disease/death indicators)
            brown_lower = np.array([10, 100, 20])
            brown_upper = np.array([20, 255, 200])
            brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)
            brown_percentage = np.sum(brown_mask > 0) / (brown_mask.shape[0] * brown_mask.shape[1])
            
            # Calculate health score
            health_score = green_percentage - (yellow_percentage * 0.5) - (brown_percentage * 0.8)
            health_score = max(0, min(1, health_score))
            
            # Determine health status
            if health_score >= self.health_thresholds['excellent']:
                health = 'excellent'
            elif health_score >= self.health_thresholds['good']:
                health = 'good'
            elif health_score >= self.health_thresholds['fair']:
                health = 'fair'
            else:
                health = 'poor'
            
            # Analyze watering needs based on color intensity
            avg_saturation = np.mean(hsv[:, :, 1])
            if avg_saturation < 100:
                watering = 'needed'
            elif avg_saturation < 150:
                watering = 'adequate'
            else:
                watering = 'excessive'
            
            # Analyze light conditions based on brightness
            avg_value = np.mean(hsv[:, :, 2])
            if avg_value < 100:
                light = 'insufficient'
            elif avg_value < 200:
                light = 'sufficient'
            else:
                light = 'excessive'
            
            # Detect issues
            issues = []
            if yellow_percentage > 0.1:
                issues.append('Yellowing detected - may need more water or nutrients')
            if brown_percentage > 0.05:
                issues.append('Browning detected - possible disease or overwatering')
            if green_percentage < 0.3:
                issues.append('Low green content - plant may be stressed')
            
            confidence = int(health_score * 100)
            
            return {
                'health': health,
                'watering': watering,
                'light': light,
                'issues': issues,
                'confidence': confidence,
                'analysis_data': {
                    'green_percentage': round(green_percentage * 100, 1),
                    'yellow_percentage': round(yellow_percentage * 100, 1),
                    'brown_percentage': round(brown_percentage * 100, 1),
                    'health_score': round(health_score * 100, 1)
                }
            }
            
        except Exception as e:
            return {
                'error': f'Analysis failed: {str(e)}',
                'health': 'unknown',
                'watering': 'unknown',
                'light': 'unknown',
                'issues': ['Analysis error occurred'],
                'confidence': 0
            }

class AICareAdvisor:
    def __init__(self):
        self.care_tips = {
            'excellent': [
                'Your plant is thriving! Maintain current care routine',
                'Continue regular watering schedule',
                'Keep in current lighting conditions',
                'Monitor for any changes'
            ],
            'good': [
                'Your plant is healthy with minor improvements possible',
                'Check soil moisture regularly',
                'Ensure adequate lighting',
                'Consider slight adjustments to watering'
            ],
            'fair': [
                'Your plant needs attention',
                'Increase watering frequency',
                'Move to better lighting',
                'Check for pests or diseases',
                'Consider repotting if needed'
            ],
            'poor': [
                'Your plant needs immediate care',
                'Water thoroughly and check drainage',
                'Move to bright, indirect light',
                'Remove any dead or diseased parts',
                'Consider professional help if condition worsens'
            ]
        }
    
    def generate_advice(self, analysis_result):
        """Generate personalized care advice based on analysis"""
        health = analysis_result.get('health', 'good')
        watering = analysis_result.get('watering', 'adequate')
        
        # Base recommendations
        recommendations = self.care_tips.get(health, self.care_tips['good'])
        
        # Watering-specific advice
        if watering == 'needed':
            recommendations.insert(0, 'Water your plant within 24 hours')
            watering_schedule = 'Water now, then every 3-4 days'
        elif watering == 'adequate':
            watering_schedule = 'Continue current watering schedule'
        else:
            recommendations.insert(0, 'Reduce watering frequency')
            watering_schedule = 'Water less frequently, allow soil to dry between watering'
        
        # Create summary
        summary = f"Your plant appears to be in {health} condition. "
        if watering == 'needed':
            summary += "It needs watering soon."
        elif watering == 'adequate':
            summary += "Watering levels are adequate."
        else:
            summary += "It may be getting too much water."
        
        return {
            'summary': summary,
            'recommendations': recommendations[:4],  # Top 4 recommendations
            'watering_schedule': watering_schedule,
            'care_tips': [
                'Use room temperature water',
                'Ensure proper drainage',
                'Avoid overwatering',
                'Monitor for pests regularly',
                'Check soil moisture before watering'
            ]
        }

# Initialize analyzers
plant_analyzer = PlantAnalyzer()
ai_advisor = AICareAdvisor()

@app.route('/api/analyze', methods=['POST'])
def analyze_plant():
    """Analyze plant image and provide care recommendations"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Analyze the image
        analysis_result = plant_analyzer.analyze_image(image_data)
        
        if 'error' in analysis_result:
            return jsonify(analysis_result), 500
        
        # Generate AI advice
        ai_advice = ai_advisor.generate_advice(analysis_result)
        
        # Combine results
        result = {
            'analysis': analysis_result,
            'ai_advice': ai_advice,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Plant Care Assistant API',
        'version': '1.0.0'
    })

@app.route('/api/plants', methods=['GET'])
def get_plant_database():
    """Get common plant care information"""
    plants = {
        'monstera': {
            'name': 'Monstera Deliciosa',
            'watering': 'Water when top 2-3 inches of soil is dry',
            'light': 'Bright, indirect light',
            'humidity': 'High humidity preferred',
            'temperature': '65-85°F (18-29°C)'
        },
        'pothos': {
            'name': 'Pothos (Epipremnum aureum)',
            'watering': 'Water when soil feels dry',
            'light': 'Low to bright indirect light',
            'humidity': 'Average humidity',
            'temperature': '60-85°F (15-29°C)'
        },
        'snake_plant': {
            'name': 'Snake Plant (Sansevieria)',
            'watering': 'Water sparingly, allow soil to dry completely',
            'light': 'Low to bright indirect light',
            'humidity': 'Low humidity tolerant',
            'temperature': '60-85°F (15-29°C)'
        }
    }
    return jsonify(plants)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
