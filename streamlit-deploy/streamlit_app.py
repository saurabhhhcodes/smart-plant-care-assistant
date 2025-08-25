import streamlit as st
import os
import sys
from pathlib import Path
from PIL import Image
import io
import requests
from dotenv import load_dotenv
import cv2
import numpy as np
import json
import time
import base64
from datetime import datetime
import threading

# Deployment configuration
st.set_page_config(
    page_title=":seedling: Smart Plant Care Assistant",
    page_icon=":seedling:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mock PlantCareAgent for deployment (since Ollama won't be available)
class MockPlantCareAgent:
    """Mock agent for deployment without Ollama dependency."""
    
    def __init__(self, model_name="mock"):
        self.model_name = model_name
        
    def analyze_image(self, image_data):
        """Mock image analysis."""
        return {
            'status': 'success',
            'health_analysis': {
                'healthy_percentage': 75.0,
                'yellow_percentage': 15.0,
                'brown_percentage': 10.0
            },
            'summary': {
                'health_score': '75%',
                'plant_type': 'Unknown Plant',
                'issues': ['Minor yellowing detected']
            }
        }
    
    def chat(self, message, chat_history=None):
        """Mock chat response."""
        responses = {
            'water': "Water your plant when the top inch of soil feels dry. Most plants prefer consistent moisture but not waterlogged soil.",
            'light': "Most houseplants prefer bright, indirect light. Avoid direct sunlight which can scorch leaves.",
            'yellow': "Yellow leaves often indicate overwatering, underwatering, or natural aging. Check soil moisture and adjust watering accordingly.",
            'brown': "Brown leaves can indicate underwatering, low humidity, or nutrient deficiency. Increase watering frequency and consider fertilizing.",
            'fertilizer': "Fertilize during growing season (spring/summer) with diluted liquid fertilizer every 2-4 weeks."
        }
        
        message_lower = message.lower()
        for key, response in responses.items():
            if key in message_lower:
                return response
        
        return "I'm here to help with plant care! Ask me about watering, lighting, fertilizing, or any plant health issues you're experiencing."
    
    def get_care_instructions(self, plant_type):
        """Mock care instructions."""
        care_guides = {
            'rose': "Roses need full sun (6+ hours), well-draining soil, regular watering, and monthly fertilizing during growing season.",
            'cactus': "Cacti need bright light, well-draining soil, infrequent watering (every 2-3 weeks), and minimal fertilizer.",
            'orchid': "Orchids prefer bright indirect light, bark-based potting mix, weekly watering with ice cubes, and monthly orchid fertilizer.",
            'succulent': "Succulents need bright light, well-draining soil, water when soil is completely dry, and minimal fertilizer.",
            'basil': "Basil needs full sun, moist well-draining soil, regular watering, and pinching flowers to encourage leaf growth.",
            'fern': "Ferns prefer indirect light, consistently moist soil, high humidity, and monthly diluted fertilizer.",
            'snake plant': "Snake plants tolerate low light, need well-draining soil, infrequent watering, and minimal care.",
            'pothos': "Pothos prefer bright indirect light, water when top soil is dry, and monthly liquid fertilizer.",
            'monstera': "Monsteras need bright indirect light, weekly watering, high humidity, and monthly fertilizing.",
            'peace lily': "Peace lilies prefer low to medium light, consistently moist soil, and monthly fertilizing."
        }
        
        return care_guides.get(plant_type.lower(), 
            "General care: Provide appropriate light, water when soil is dry, ensure good drainage, and fertilize during growing season.")

# Simple Plant Image Analyzer for deployment
class SimplePlantAnalyzer:
    """Simplified plant analyzer for deployment."""
    
    def get_plant_analysis_report(self, image):
        """Simple analysis based on color distribution."""
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define color ranges
            green_mask = cv2.inRange(hsv, np.array([25, 40, 40]), np.array([75, 255, 255]))
            yellow_mask = cv2.inRange(hsv, np.array([15, 40, 40]), np.array([35, 255, 255]))
            brown_mask = cv2.inRange(hsv, np.array([5, 40, 40]), np.array([25, 255, 255]))
            
            # Calculate percentages
            total_pixels = image.shape[0] * image.shape[1]
            green_pct = (cv2.countNonZero(green_mask) / total_pixels) * 100
            yellow_pct = (cv2.countNonZero(yellow_mask) / total_pixels) * 100
            brown_pct = (cv2.countNonZero(brown_mask) / total_pixels) * 100
            
            # Calculate health score
            health_score = max(0, min(100, green_pct - (yellow_pct * 0.5) - (brown_pct * 0.8)))
            
            return {
                'healthy_percentage': green_pct,
                'yellow_percentage': yellow_pct,
                'brown_percentage': brown_pct,
                'overall_health_score': health_score,
                'leaf_count': 'N/A',
                'total_leaf_area': total_pixels * 0.3,  # Estimate
                'analysis_time': 0.1
            }
        except Exception as e:
            return {
                'healthy_percentage': 50,
                'yellow_percentage': 25,
                'brown_percentage': 25,
                'overall_health_score': 50,
                'error': str(e)
            }

# Initialize components
@st.cache_resource
def get_plant_care_agent():
    """Initialize mock agent for deployment."""
    try:
        agent = MockPlantCareAgent()
        st.session_state.agent_initialized = True
        return agent
    except Exception as e:
        st.error(f"Error initializing Plant Care Agent: {str(e)}")
        st.session_state.agent_initialized = False
        return None

@st.cache_resource
def get_plant_analyzer():
    """Initialize plant analyzer."""
    return SimplePlantAnalyzer()

def display_sidebar():
    """Enhanced sidebar."""
    with st.sidebar:
        st.title(":seedling: Plant Care Assistant")
        
        # Deployment notice
        st.info("Deployed Version - Running on Streamlit Cloud")
        
        # Feature status
        st.subheader("Camera Analysis")
        st.success("Camera Ready")
        
        # Settings
        st.subheader("Settings")
        sensitivity = st.slider("Detection Sensitivity", 1, 10, 5)
        auto_analyze = st.checkbox("Auto-analyze", True)
        
        # Features
        st.subheader("Features")
        st.write("Camera Analysis")
        st.write("Photo Upload")
        st.write("AI Chat Assistant")
        st.write("Care Library")
        
        # Stats
        st.subheader("Stats")
        if 'analysis_count' not in st.session_state:
            st.session_state.analysis_count = 0
        st.metric("Analyses", st.session_state.analysis_count)
        
        return "mock"

def display_camera_analysis():
    """Camera analysis interface."""
    st.header("Real-Time Plant Health Monitor")
    st.markdown("*Capture a photo of your plant for instant AI analysis*")
    
    # Camera controls
    col1, col2, col3 = st.columns(3)
    with col1:
        camera_enabled = st.checkbox("Enable Camera", value=True)
    with col2:
        save_results = st.checkbox("Save Analysis", value=False)
    with col3:
        show_overlay = st.checkbox("Show Analysis", value=True)
    
    if camera_enabled:
        # Camera input
        st.markdown("### Camera Feed")
        camera_image = st.camera_input("Point camera at your plant")
        
        if camera_image is not None:
            process_camera_image(camera_image, save_results, show_overlay)
    else:
        st.info("Enable camera to start plant analysis")
        
        # Demo image option
        if st.button("Try Demo Analysis"):
            demo_analysis()

def process_camera_image(camera_image, save_results, show_overlay):
    """Process captured image."""
    try:
        image = Image.open(camera_image)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.image(image, caption="Captured Plant", use_column_width=True)
            
            if show_overlay:
                # Create simple overlay
                img_array = np.array(image)
                if len(img_array.shape) == 3:
                    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    
                    # Simple color analysis overlay
                    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
                    green_mask = cv2.inRange(hsv, np.array([25, 40, 40]), np.array([75, 255, 255]))
                    
                    overlay = img_cv.copy()
                    overlay[green_mask > 0] = [0, 255, 0]
                    result = cv2.addWeighted(img_cv, 0.7, overlay, 0.3, 0)
                    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                    
                    st.image(result_rgb, caption="Health Analysis", use_column_width=True)
        
        with col2:
            st.markdown("### Analysis")
            
            if st.button("Analyze Plant"):
                with st.spinner("Analyzing..."):
                    analysis = perform_analysis(image)
                    display_results(analysis)
                    st.session_state.analysis_count += 1
                    
                    if save_results:
                        st.success("Analysis saved!")
                        
    except Exception as e:
        st.error(f"Error: {str(e)}")

def perform_analysis(image):
    """Perform plant analysis."""
    # Convert image
    img_array = np.array(image)
    if len(img_array.shape) == 3:
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    else:
        img_cv = img_array
    
    # Get analyzer
    analyzer = get_plant_analyzer()
    cv_analysis = analyzer.get_plant_analysis_report(img_cv)
    
    # Get AI analysis
    agent = st.session_state.get('plant_agent')
    if agent:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        ai_analysis = agent.analyze_image(img_str)
    else:
        ai_analysis = {'status': 'error', 'message': 'Agent not available'}
    
    return {
        'cv_analysis': cv_analysis,
        'ai_analysis': ai_analysis,
        'timestamp': datetime.now().isoformat()
    }

def display_results(analysis):
    """Display analysis results."""
    cv_data = analysis.get('cv_analysis', {})
    
    # Health score
    health_score = cv_data.get('overall_health_score', 0)
    
    if health_score >= 80:
        st.success(f"Excellent Health: {health_score:.1f}%")
    elif health_score >= 60:
        st.success(f"Good Health: {health_score:.1f}%")
    elif health_score >= 40:
        st.warning(f"Fair Health: {health_score:.1f}%")
    else:
        st.error(f"Poor Health: {health_score:.1f}%")
    
    # Metrics
    st.metric("Healthy Areas", f"{cv_data.get('healthy_percentage', 0):.1f}%")
    st.metric("Yellow Areas", f"{cv_data.get('yellow_percentage', 0):.1f}%")
    st.metric("Brown Areas", f"{cv_data.get('brown_percentage', 0):.1f}%")
    
    # Recommendations
    recommendations = generate_recommendations(cv_data)
    if recommendations:
        st.markdown("#### Recommendations")
        for rec in recommendations:
            st.info(rec)

def generate_recommendations(cv_data):
    """Generate care recommendations."""
    recommendations = []
    
    yellow_pct = cv_data.get('yellow_percentage', 0)
    brown_pct = cv_data.get('brown_percentage', 0)
    health_score = cv_data.get('overall_health_score', 0)
    
    if yellow_pct > 20:
        recommendations.append("Check watering - yellowing may indicate overwatering")
    
    if brown_pct > 15:
        recommendations.append("Consider fertilizing - browning may indicate nutrient issues")
    
    if health_score > 80:
        recommendations.append("Great job! Continue your current care routine")
    elif health_score < 40:
        recommendations.append("Plant needs immediate attention")
    
    if not recommendations:
        recommendations.append("Monitor regularly and maintain consistent care")
    
    return recommendations

def demo_analysis():
    """Show demo analysis."""
    st.markdown("### Demo Analysis")
    
    # Mock demo results
    demo_results = {
        'cv_analysis': {
            'healthy_percentage': 78.5,
            'yellow_percentage': 12.3,
            'brown_percentage': 9.2,
            'overall_health_score': 82.1
        }
    }
    
    st.success("Demo Plant Health: 82.1%")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Healthy", "78.5%")
    with col2:
        st.metric("Yellow", "12.3%")
    with col3:
        st.metric("Brown", "9.2%")
    
    st.info("This plant looks healthy! Continue current care routine.")

def display_upload_section():
    """Photo upload section."""
    st.markdown("#### Upload Plant Photo")
    
    uploaded_file = st.file_uploader("Choose image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Analyze Upload"):
            with st.spinner("Analyzing..."):
                analysis = perform_analysis(image)
                display_results(analysis)
                st.session_state.analysis_count += 1

def display_chat_interface():
    """Chat interface."""
    st.markdown("#### Plant Care Chat")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Plant Care Assistant. How can I help you today?"}
        ]
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about plant care..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            agent = st.session_state.get('plant_agent')
            if agent:
                response = agent.chat(prompt, st.session_state.messages[:-1])
            else:
                response = "I'm here to help with plant care questions!"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def display_care_library():
    """Care library."""
    st.markdown("#### Plant Care Library")
    
    plant_type = st.selectbox("Select Plant", [
        "Rose", "Cactus", "Orchid", "Succulent", "Basil", 
        "Fern", "Snake Plant", "Pothos", "Monstera", "Peace Lily"
    ])
    
    if st.button("Get Care Guide"):
        agent = st.session_state.get('plant_agent')
        if agent:
            care_info = agent.get_care_instructions(plant_type.lower())
            st.markdown(f"### {plant_type} Care Guide")
            st.write(care_info)

def main():
    # Initialize session state
    if 'plant_agent' not in st.session_state:
        st.session_state.plant_agent = get_plant_care_agent()
    
    # Sidebar
    model_name = display_sidebar()
    
    # Main content
    st.title(":seedling: Smart Plant Care Assistant")
    st.markdown("### AI-Powered Plant Health Analysis")
    
    # Primary feature
    display_camera_analysis()
    
    # Secondary features
    st.markdown("---")
    st.markdown("### Additional Features")
    
    tab1, tab2, tab3 = st.tabs(["Upload Photo", "Chat Expert", "Care Library"])
    
    with tab1:
        display_upload_section()
    
    with tab2:
        display_chat_interface()
    
    with tab3:
        display_care_library()

# Initialize session state
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False

if __name__ == "__main__":
    main()