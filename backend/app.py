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

class PlantDetector:
    def __init__(self):
        self.plant_indicators = {
            'monstera': {
                'name': 'Monstera Deliciosa',
                'common_name': 'Swiss Cheese Plant',
                'features': ['large leaves', 'holes in leaves', 'split leaves'],
                'color_range': {'green': [35, 50, 50], 'dark_green': [25, 40, 40]}
            },
            'pothos': {
                'name': 'Epipremnum aureum',
                'common_name': 'Pothos or Devil\'s Ivy',
                'features': ['heart-shaped leaves', 'trailing vines', 'variegated'],
                'color_range': {'green': [35, 50, 50], 'yellow_green': [30, 45, 45]}
            },
            'snake_plant': {
                'name': 'Sansevieria trifasciata',
                'common_name': 'Snake Plant or Mother-in-law\'s Tongue',
                'features': ['upright leaves', 'striped pattern', 'thick leaves'],
                'color_range': {'green': [35, 50, 50], 'dark_green': [25, 40, 40]}
            },
            'ficus': {
                'name': 'Ficus lyrata',
                'common_name': 'Fiddle Leaf Fig',
                'features': ['large fiddle-shaped leaves', 'tree-like'],
                'color_range': {'green': [35, 50, 50], 'dark_green': [25, 40, 40]}
            },
            'aloe': {
                'name': 'Aloe vera',
                'common_name': 'Aloe Vera',
                'features': ['succulent leaves', 'spiky edges', 'thick leaves'],
                'color_range': {'green': [35, 50, 50], 'blue_green': [40, 55, 55]}
            },
            'cactus': {
                'name': 'Various Cactaceae',
                'common_name': 'Cactus',
                'features': ['spiky', 'cylindrical', 'succulent'],
                'color_range': {'green': [35, 50, 50], 'blue_green': [40, 55, 55]}
            }
        }
    
    def detect_plant(self, image_np):
        """Detect if image contains a plant and identify species"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            
            # Calculate green percentage (basic plant detection)
            green_lower = np.array([35, 50, 50])
            green_upper = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            green_percentage = np.sum(green_mask > 0) / (green_mask.shape[0] * green_mask.shape[1])
            
            # If green percentage is too low, it's probably not a plant
            if green_percentage < 0.1:
                return {
                    'is_plant': False,
                    'confidence': 0,
                    'message': 'No plant detected in the image. Please take a photo of a plant.'
                }
            
            # Analyze shape and texture for plant identification
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            
            # Edge detection for leaf analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Contour analysis for leaf shape
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze contours for plant-like features
            plant_features = self.analyze_plant_features(contours, hsv, edge_density)
            
            # Identify most likely plant species
            plant_identification = self.identify_plant_species(plant_features, hsv)
            
            return {
                'is_plant': True,
                'confidence': min(95, int(green_percentage * 100)),
                'plant_info': plant_identification,
                'features_detected': plant_features
            }
            
        except Exception as e:
            return {
                'is_plant': False,
                'confidence': 0,
                'message': f'Error analyzing image: {str(e)}'
            }
    
    def analyze_plant_features(self, contours, hsv, edge_density):
        """Analyze contours for plant-specific features"""
        features = []
        
        if len(contours) > 0:
            # Find largest contour (likely the main plant)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area > 1000:  # Significant plant area
                # Analyze shape
                perimeter = cv2.arcLength(largest_contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    
                    if circularity < 0.3:
                        features.append('elongated_leaves')
                    elif circularity > 0.7:
                        features.append('round_leaves')
                    
                    # Check for holes (Monstera-like)
                    if edge_density > 0.05:
                        features.append('detailed_leaf_structure')
                
                # Analyze color distribution
                avg_saturation = np.mean(hsv[:, :, 1])
                avg_value = np.mean(hsv[:, :, 2])
                
                if avg_saturation > 100:
                    features.append('vibrant_green')
                if avg_value > 150:
                    features.append('bright_leaves')
        
        return features
    
    def identify_plant_species(self, features, hsv):
        """Identify plant species based on detected features"""
        scores = {}
        
        for plant_type, plant_data in self.plant_indicators.items():
            score = 0
            
            # Score based on features
            for feature in features:
                if feature in plant_data['features']:
                    score += 20
            
            # Score based on color
            green_lower = np.array(plant_data['color_range']['green'])
            green_upper = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            green_percentage = np.sum(green_mask > 0) / (green_mask.shape[0] * green_mask.shape[1])
            score += green_percentage * 50
            
            scores[plant_type] = score
        
        # Find best match
        if scores:
            best_match = max(scores, key=scores.get)
            best_score = scores[best_match]
            
            if best_score > 30:
                plant_info = self.plant_indicators[best_match]
                return {
                    'species': plant_info['name'],
                    'common_name': plant_info['common_name'],
                    'confidence': min(95, int(best_score)),
                    'type': best_match
                }
        
        # Default to generic plant if no specific match
        return {
            'species': 'Unknown Plant',
            'common_name': 'House Plant',
            'confidence': 50,
            'type': 'generic'
        }

class PlantAnalyzer:
    def __init__(self):
        self.health_thresholds = {
            'excellent': 0.8,
            'good': 0.6,
            'fair': 0.4,
            'poor': 0.2
        }
        self.plant_detector = PlantDetector()
    
    def analyze_image(self, image_data):
        """Analyze plant image for health indicators"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            
            # First, detect if it's a plant
            plant_detection = self.plant_detector.detect_plant(image_np)
            
            if not plant_detection['is_plant']:
                return {
                    'error': plant_detection['message'],
                    'health': 'unknown',
                    'watering': 'unknown',
                    'light': 'unknown',
                    'issues': ['Not a plant image'],
                    'confidence': 0
                }
            
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
                'plant_info': plant_detection['plant_info'],
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
            'monstera': {
                'excellent': [
                    'Your Monstera is thriving! Keep up the excellent care',
                    'Continue regular watering when top soil feels dry',
                    'Maintain bright, indirect light',
                    'Consider repotting if it outgrows its container'
                ],
                'good': [
                    'Your Monstera is healthy with room for improvement',
                    'Water when top 2-3 inches of soil is dry',
                    'Ensure bright, indirect light',
                    'Mist leaves occasionally for humidity'
                ],
                'fair': [
                    'Your Monstera needs some attention',
                    'Increase humidity with a humidifier or misting',
                    'Check for pests on the underside of leaves',
                    'Consider moving to brighter indirect light'
                ],
                'poor': [
                    'Your Monstera needs immediate care',
                    'Check for root rot and repot if necessary',
                    'Move to bright, indirect light',
                    'Water thoroughly and ensure proper drainage'
                ]
            },
            'pothos': {
                'excellent': [
                    'Your Pothos is flourishing! Maintain current care',
                    'Water when soil feels dry to the touch',
                    'Keep in bright, indirect light',
                    'Trim long vines to encourage bushier growth'
                ],
                'good': [
                    'Your Pothos is healthy and growing well',
                    'Water when top inch of soil is dry',
                    'Provide bright, indirect light',
                    'Fertilize monthly during growing season'
                ],
                'fair': [
                    'Your Pothos needs some TLC',
                    'Increase watering frequency slightly',
                    'Move to brighter location',
                    'Check for pests and remove dead leaves'
                ],
                'poor': [
                    'Your Pothos needs immediate attention',
                    'Water thoroughly and check drainage',
                    'Move to bright, indirect light',
                    'Remove any yellow or dead leaves'
                ]
            },
            'snake_plant': {
                'excellent': [
                    'Your Snake Plant is thriving! Perfect low-maintenance plant',
                    'Water sparingly - only when soil is completely dry',
                    'Tolerates low light but prefers bright indirect light',
                    'Repot only when rootbound'
                ],
                'good': [
                    'Your Snake Plant is healthy and resilient',
                    'Water only when soil is completely dry',
                    'Can tolerate low light conditions',
                    'Avoid overwatering - this plant prefers neglect'
                ],
                'fair': [
                    'Your Snake Plant needs minimal care',
                    'Reduce watering frequency',
                    'Move to brighter location if possible',
                    'Check for root rot from overwatering'
                ],
                'poor': [
                    'Your Snake Plant needs immediate care',
                    'Stop watering immediately - likely overwatered',
                    'Move to bright, indirect light',
                    'Repot in well-draining soil if necessary'
                ]
            }
        }
        
        # Generic care tips for unknown plants
        self.generic_care = {
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
        plant_info = analysis_result.get('plant_info', {})
        plant_type = plant_info.get('type', 'generic')
        
        # Get plant-specific care tips
        if plant_type in self.care_tips and health in self.care_tips[plant_type]:
            recommendations = self.care_tips[plant_type][health]
        else:
            recommendations = self.generic_care.get(health, self.generic_care['good'])
        
        # Watering-specific advice
        if watering == 'needed':
            recommendations.insert(0, 'Water your plant within 24 hours')
            watering_schedule = 'Water now, then every 3-4 days'
        elif watering == 'adequate':
            watering_schedule = 'Continue current watering schedule'
        else:
            recommendations.insert(0, 'Reduce watering frequency')
            watering_schedule = 'Water less frequently, allow soil to dry between watering'
        
        # Create summary with plant name
        plant_name = plant_info.get('common_name', 'plant')
        summary = f"Your {plant_name} appears to be in {health} condition. "
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
            'common_name': 'Swiss Cheese Plant',
            'watering': 'Water when top 2-3 inches of soil is dry',
            'light': 'Bright, indirect light',
            'humidity': 'High humidity preferred',
            'temperature': '65-85°F (18-29°C)'
        },
        'pothos': {
            'name': 'Epipremnum aureum',
            'common_name': 'Pothos or Devil\'s Ivy',
            'watering': 'Water when soil feels dry',
            'light': 'Low to bright indirect light',
            'humidity': 'Average humidity',
            'temperature': '60-85°F (15-29°C)'
        },
        'snake_plant': {
            'name': 'Sansevieria trifasciata',
            'common_name': 'Snake Plant or Mother-in-law\'s Tongue',
            'watering': 'Water sparingly, allow soil to dry completely',
            'light': 'Low to bright indirect light',
            'humidity': 'Low humidity tolerant',
            'temperature': '60-85°F (15-29°C)'
        }
    }
    return jsonify(plants)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
