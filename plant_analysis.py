import cv2
import numpy as np
from typing import Dict

class PlantImageAnalyzer:
    """Performs plant health and disease analysis using OpenCV."""

    def detect_plant(self, img: np.ndarray) -> bool:
        """Detect if a plant is present in the image based on a wider range of plant-like colors."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define a wider range of plant-like colors (greens, reds, purples, yellows)
        # Green mask
        green_mask = cv2.inRange(hsv, (30, 40, 40), (90, 255, 255))
        # Red mask (for red-leafed plants)
        red_mask1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))
        red_mask2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        # Purple mask
        purple_mask = cv2.inRange(hsv, (125, 50, 50), (160, 255, 255))
        # Yellow mask
        yellow_mask = cv2.inRange(hsv, (15, 50, 50), (35, 255, 255))

        # Combine all color masks
        combined_mask = cv2.bitwise_or(green_mask, red_mask)
        combined_mask = cv2.bitwise_or(combined_mask, purple_mask)
        combined_mask = cv2.bitwise_or(combined_mask, yellow_mask)

        # Calculate the percentage of plant-like pixels
        plant_percentage = (cv2.countNonZero(combined_mask) / (img.shape[0] * img.shape[1])) * 100
        
        # If the percentage is above a threshold, assume a plant is present
        return plant_percentage > 5  # Threshold of 5% plant-like pixels

    def get_chlorophyll_info(self) -> str:
        """Return information about chlorophyll."""
        return (
            "Chlorophyll is the primary pigment in most plants, responsible for their green color. "
            "It plays a crucial role in photosynthesis, the process of converting light energy into chemical energy. "
            "While most plants are green due to chlorophyll, some plants have other pigments that can mask the green color, "
            "leading to red, purple, or yellow leaves. These plants still have chlorophyll and photosynthesize."
        )

    def analyze_plant_health(self, img: np.ndarray) -> Dict:
        """Analyze plant health based on color segmentation, including a wider range of healthy colors."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define masks for various healthy plant colors (green, red, purple)
        # Green mask
        green_mask = cv2.inRange(hsv, (30, 40, 40), (90, 255, 255))
        # Red mask (for red-leafed plants)
        red_mask1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))
        red_mask2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        # Purple mask
        purple_mask = cv2.inRange(hsv, (125, 50, 50), (160, 255, 255))
        
        # Combine healthy masks
        healthy_mask = cv2.bitwise_or(green_mask, red_mask)
        healthy_mask = cv2.bitwise_or(healthy_mask, purple_mask)
        
        # Yellow mask for potentially unhealthy parts
        yellow_mask = cv2.inRange(hsv, (15, 50, 50), (35, 255, 255))
        # Brown mask for dead or dying parts
        brown_mask = cv2.inRange(hsv, (10, 100, 20), (20, 255, 200))
        
        total_pixels = img.shape[0] * img.shape[1]
        
        # Calculate percentages
        healthy_pct = (cv2.countNonZero(healthy_mask) / total_pixels) * 100
        yellow_pct = (cv2.countNonZero(yellow_mask) / total_pixels) * 100
        brown_pct = (cv2.countNonZero(brown_mask) / total_pixels) * 100
        
        return {
            'healthy_percentage': healthy_pct,
            'yellow_percentage': yellow_pct,
            'brown_percentage': brown_pct,
        }

    def detect_diseases(self, img: np.ndarray) -> Dict:
        # Placeholder: No real disease detection, just a stub
        return {
            'powdery_mildew_percentage': 0.0,
            'leaf_spot_percentage': 0.0,
            'blight_percentage': 0.0
        }

    def analyze_video(self, video_path: str) -> Dict:
        # Example: Analyze the first frame of a video
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return {'status': 'error', 'message': 'Could not read video.'}
        return self.analyze_plant_health(frame)
