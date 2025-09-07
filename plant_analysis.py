import cv2
import numpy as np
from typing import Dict

class PlantImageAnalyzer:
    """Performs plant health and disease analysis using OpenCV."""

    def _enhance_image(self, img: np.ndarray) -> np.ndarray:
        """Applies an advanced image enhancement pipeline."""
        # Resize image for faster processing
        img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)

        # 1. Auto-Brightness and Contrast using CLAHE
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # 2. Advanced Sharpening
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        enhanced_img = cv2.filter2D(enhanced_img, -1, sharpen_kernel)
        
        return enhanced_img

    def detect_plant(self, img: np.ndarray) -> bool:
        """Detect if a plant is present in the image."""
        enhanced_img = self._enhance_image(img)
        hsv = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2HSV)
        # Green mask to identify plant-like colors
        green_mask = cv2.inRange(hsv, (36, 25, 25), (86, 255, 255))
        # Calculate the percentage of green pixels
        green_percentage = (cv2.countNonZero(green_mask) / (img.shape[0] * img.shape[1])) * 100
        # If green percentage is above a threshold, assume a plant is present
        return green_percentage > 5  # Threshold of 5% green pixels

    def analyze_plant_health(self, img: np.ndarray) -> Dict:
        # Example: Simple color thresholding for green, yellow, brown
        enhanced_img = self._enhance_image(img)
        hsv = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2HSV)
        # Green mask
        green_mask = cv2.inRange(hsv, (36, 25, 25), (86, 255, 255))
        # Yellow mask
        yellow_mask = cv2.inRange(hsv, (15, 50, 50), (35, 255, 255))
        # Brown mask (approximate)
        brown_mask = cv2.inRange(hsv, (10, 100, 20), (20, 255, 200))
        total = enhanced_img.shape[0] * enhanced_img.shape[1]
        green_pct = 100 * np.sum(green_mask > 0) / total
        yellow_pct = 100 * np.sum(yellow_mask > 0) / total
        brown_pct = 100 * np.sum(brown_mask > 0) / total
        healthy_pct = green_pct
        return {
            'healthy_percentage': healthy_pct,
            'yellow_percentage': yellow_pct,
            'brown_percentage': brown_pct
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
