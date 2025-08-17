import cv2
import numpy as np
from typing import Dict, Tuple, List, Optional
import matplotlib.pyplot as plt
from PIL import Image
import io

class PlantImageAnalyzer:
    def __init__(self):
        self.default_blur = (5, 5)
        self.default_threshold = 100
        self.leaf_area_pixels = 0
        self.leaf_contours = []
        self.leaf_holes = []
        
    def analyze_plant_health(self, image: np.ndarray) -> Dict:
        """
        Analyze plant health from an image
        Returns a dictionary with analysis results
        """
        # Convert to grayscale and apply blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, self.default_blur, 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 30, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size to find leaves
        min_contour_area = 500
        leaf_contours = [c for c in contours if cv2.contourArea(c) > min_contour_area]
        
        # Calculate total leaf area
        total_leaf_area = sum(cv2.contourArea(c) for c in leaf_contours)
        
        # Analyze color distribution (health indicator)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for healthy and unhealthy leaves
        healthy_green_low = np.array([25, 40, 40])
        healthy_green_high = np.array([75, 255, 255])
        unhealthy_yellow_low = np.array([15, 40, 40])
        unhealthy_yellow_high = np.array([35, 255, 255])
        unhealthy_brown_low = np.array([5, 40, 40])
        unhealthy_brown_high = np.array([25, 255, 255])
        
        # Create masks for different colors
        healthy_mask = cv2.inRange(hsv, healthy_green_low, healthy_green_high)
        yellow_mask = cv2.inRange(hsv, unhealthy_yellow_low, unhealthy_yellow_high)
        brown_mask = cv2.inRange(hsv, unhealthy_brown_low, unhealthy_brown_high)
        
        # Calculate areas
        healthy_area = cv2.countNonZero(healthy_mask)
        yellow_area = cv2.countNonZero(yellow_mask)
        brown_area = cv2.countNonZero(brown_mask)
        total_plant_area = healthy_area + yellow_area + brown_area
        
        # Calculate health metrics
        health_metrics = {
            'healthy_percentage': (healthy_area / total_plant_area) * 100 if total_plant_area > 0 else 0,
            'yellow_percentage': (yellow_area / total_plant_area) * 100 if total_plant_area > 0 else 0,
            'brown_percentage': (brown_area / total_plant_area) * 100 if total_plant_area > 0 else 0,
            'total_leaf_area': total_leaf_area,
            'leaf_count': len(leaf_contours),
        }
        
        return health_metrics
    
    def detect_diseases(self, image: np.ndarray) -> Dict:
        """
        Detect common plant diseases using color and texture analysis
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for common disease symptoms
        # These are example values and should be fine-tuned
        disease_masks = {
            'yellow_rust': cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255])),
            'brown_spot': cv2.inRange(hsv, np.array([5, 50, 50]), np.array([15, 255, 255])),
            'powdery_mildew': cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))
        }
        
        # Calculate affected areas
        total_pixels = image.shape[0] * image.shape[1]
        disease_metrics = {}
        
        for disease, mask in disease_masks.items():
            affected_area = cv2.countNonZero(mask)
            disease_metrics[f'{disease}_area'] = affected_area
            disease_metrics[f'{disease}_percentage'] = (affected_area / total_pixels) * 100
        
        return disease_metrics
    
    def get_plant_analysis_report(self, image: np.ndarray) -> Dict:
        """
        Generate a comprehensive plant analysis report
        """
        health_metrics = self.analyze_plant_health(image)
        disease_metrics = self.detect_diseases(image)
        
        # Combine all metrics
        analysis_report = {
            **health_metrics,
            **disease_metrics,
            'overall_health_score': self.calculate_health_score(health_metrics, disease_metrics)
        }
        
        return analysis_report
    
    def calculate_health_score(self, health_metrics: Dict, disease_metrics: Dict) -> float:
        """
        Calculate an overall health score (0-100)
        Higher score means healthier plant
        """
        # Base score from healthy area percentage
        score = health_metrics.get('healthy_percentage', 0)
        
        # Penalize for disease presence
        disease_penalty = sum(
            pct for key, pct in disease_metrics.items() 
            if key.endswith('_percentage')
        ) * 0.5  # Reduce penalty factor as needed
        
        score = max(0, min(100, score - disease_penalty))
        return round(score, 2)
    
    def get_visual_analysis(self, image: np.ndarray) -> np.ndarray:
        """
        Generate a visualization of the analysis
        """
        # Create a copy of the image for visualization
        vis = image.copy()
        
        # Convert to grayscale and find edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 30, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours
        cv2.drawContours(vis, contours, -1, (0, 255, 0), 2)
        
        # Add health metrics as text
        health_metrics = self.analyze_plant_health(image)
        text_y = 30
        cv2.putText(vis, f"Health Score: {health_metrics.get('healthy_percentage', 0):.1f}%", 
                   (10, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return vis
    
    @staticmethod
    def image_to_bytes(image: np.ndarray) -> bytes:
        """Convert numpy image to bytes"""
        _, buffer = cv2.imencode('.png', image)
        return buffer.tobytes()
    
    @staticmethod
    def bytes_to_image(image_bytes: bytes) -> np.ndarray:
        """Convert bytes to numpy image"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
