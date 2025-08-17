import streamlit as st
import os
from PIL import Image
import io
import requests
from dotenv import load_dotenv
import cv2
import numpy as np
from plant_care_agent import PlantCareAgent
import json
import time
import base64
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize the Plant Care Agent with Ollama
@st.cache_resource
def get_plant_care_agent():
    try:
        return PlantCareAgent(model_name="llama3")  # or any other model you have downloaded
    except Exception as e:
        st.error(f"Error initializing Plant Care Agent: {str(e)}")
        st.error("Make sure Ollama is installed and running with the 'llama3' model downloaded.")
        return None

# Set page config
st.set_page_config(
    page_title="🌱 Smart Plant Care Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'plant_agent' not in st.session_state:
    st.session_state.plant_agent = get_plant_care_agent()

# Title and description
st.title("🌱 Smart Plant Care Assistant")
st.markdown("""
Welcome to the Smart Plant Care Assistant! Upload a photo of your plant 
and get instant analysis and care recommendations.
""")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    st.info("Using local Ollama model (llama3)")
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["llama3", "mistral", "gemma"],  # Add other models you have downloaded
        index=0,
        help="Select the local Ollama model to use for analysis"
    )
    
    # Information about Ollama
    with st.expander("About Ollama"):
        st.markdown("""
        This app uses Ollama to run local LLMs. To use this app:
        1. Install [Ollama](https://ollama.ai/)
        2. Download a model: `ollama pull llama3`
        3. Make sure Ollama is running locally
        """)

# Main content
st.header("🌿 Plant Analysis")

# Tabs for different input methods
tab1, tab2 = st.tabs(["📷 Camera Analysis", "📁 Upload Photo"])

with tab1:
    st.subheader("Real-time Camera Analysis")
    
    # Initialize camera state
    if 'camera_on' not in st.session_state:
        st.session_state.camera_on = False
        st.session_state.last_analysis = None
        st.session_state.last_frame = None
        st.session_state.analysis_interval = 10  # seconds between analyses
        st.session_state.last_analysis_time = 0
    
    # Camera controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎥 Toggle Camera"):
            st.session_state.camera_on = not st.session_state.camera_on
            if not st.session_state.camera_on:
                st.session_state.last_frame = None
    
    with col2:
        st.session_state.analysis_interval = st.slider(
            "Analysis Frequency (seconds)",
            min_value=2,
            max_value=30,
            value=10,
            help="How often to analyze the plant (lower = more frequent but more resource-intensive)"
        )
    
    # Camera capture and analysis
    if st.session_state.camera_on:
        camera_img = st.camera_input("Take a picture of your plant")
        
        if camera_img is not None:
            # Read and process the image
            image = Image.open(camera_img)
            st.session_state.uploaded_image = image
            img_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV if needed
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Update the last frame
            st.session_state.last_frame = img_array
            st.session_state.image_array = img_array
            
            # Check if it's time for a new analysis
            current_time = time.time()
            if (current_time - st.session_state.get('last_analysis_time', 0)) > st.session_state.analysis_interval:
                with st.spinner("Analyzing plant..."):
                    try:
                        # Convert to base64 for the agent
                        buffered = io.BytesIO()
                        image.save(buffered, format="JPEG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        
                        # Get analysis from the agent
                        if st.session_state.plant_agent:
                            analysis = st.session_state.plant_agent.analyze_plant_image(img_str)
                            if analysis.get("status") == "success":
                                st.session_state.analysis_result = {
                                    "health_status": analysis.get("analysis", {}).get("health_status", "Unknown"),
                                    "plant_type": analysis.get("analysis", {}).get("plant_type", "Unknown"),
                                    "confidence": analysis.get("analysis", {}).get("confidence", 0.0),
                                    "issues": analysis.get("analysis", {}).get("issues", []),
                                    "care_advice": analysis.get("analysis", {}).get("recommendations", []),
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                st.session_state.last_analysis_time = current_time
                                st.rerun()  # Refresh to show analysis
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
    else:
        st.info("Click 'Toggle Camera' to start analyzing plants with your camera")

with tab2:
    st.subheader("Upload Plant Photo")
    uploaded_file = st.file_uploader(
        "Choose an image...", 
        type=["jpg", "jpeg", "png"],
        help="Upload a clear photo of your plant"
    )
    
    if uploaded_file is not None:
        # Read image file
        image = Image.open(uploaded_file)
        st.session_state.uploaded_image = image
        
        # Display the uploaded image
        st.image(image, caption="Uploaded Plant", use_column_width=True)
        
        # Convert to OpenCV format for processing
        img_array = np.array(image)
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Save to session state for processing
        st.session_state.image_array = img_array
        
        # Add manual analysis button
        if st.button("🔍 Analyze Plant"):
            with st.spinner("Analyzing plant..."):
                try:
                    # Convert to base64 for the agent
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Get analysis from the agent
                    if st.session_state.plant_agent:
                        analysis = st.session_state.plant_agent.analyze_plant_image(img_str)
                        if analysis.get("status") == "success":
                            st.session_state.analysis_result = {
                                "health_status": analysis.get("analysis", {}).get("health_status", "Unknown"),
                                "plant_type": analysis.get("analysis", {}).get("plant_type", "Unknown"),
                                "confidence": analysis.get("analysis", {}).get("confidence", 0.0),
                                "issues": analysis.get("analysis", {}).get("issues", []),
                                "care_advice": analysis.get("analysis", {}).get("recommendations", []),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")

# Display analysis results
if 'analysis_result' in st.session_state and st.session_state.analysis_result:
    with st.expander("📊 Analysis Results", expanded=True):
        result = st.session_state.analysis_result
        
        # Health status with color coding
        health_color = "green" if "healthy" in str(result["health_status"]).lower() else "red"
        st.markdown(f"### Health Status: :{health_color}[{result['health_status']}]")
        
        # Display plant type and confidence
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Plant Type", result["plant_type"])
        with col2:
            st.metric("Confidence", f"{result['confidence']*100:.1f}%")
        
        # Display issues if any
        if result.get("issues"):
            st.subheader("Potential Issues")
            for issue in result["issues"]:
                st.warning(f"⚠️ {issue}")
        
        # Display care advice
        if result.get("care_advice"):
            st.subheader("Care Recommendations")
            for advice in result["care_advice"]:
                st.success(f"🌱 {advice}")
        
        # Show timestamp
        if "timestamp" in result:
            st.caption(f"Last analyzed: {result['timestamp']}")

# Add necessary imports at the top of the file if not already present
# import time
# import base64
# import io
# from datetime import datetime

# Add a chat interface for plant care questions
st.markdown("---")
st.subheader("Ask the Plant Care Expert")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], str):
            st.markdown(message["content"])
        elif isinstance(message["content"], dict):
            st.json(message["content"], expanded=False)

# Chat input
if prompt := st.chat_input("Ask me anything about plant care..."):
    if not st.session_state.plant_agent:
        st.error("Failed to initialize the Plant Care Agent. Please make sure Ollama is running and the model is downloaded.")
        st.stop()
    
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from the agent
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                # If there's an uploaded image, include it in the analysis
                if st.session_state.uploaded_image is not None:
                    # Convert image to base64 for the agent
                    import base64
                    from io import BytesIO
                    
                    buffered = BytesIO()
                    st.session_state.uploaded_image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Process the image with the agent
                    response = st.session_state.plant_agent.process_query(
                        query=prompt,
                        image_data=img_str
                    )
                else:
                    # Regular text-based response
                    response = st.session_state.plant_agent.chat(prompt)
                
                # Display the response
                if isinstance(response, dict):
                    # If the response is a dictionary (like analysis results), display it as JSON
                    st.json(response, expanded=False)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                else:
                    # Regular text response
                    st.markdown(response)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.error(error_msg)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_msg
            })
    
    if st.session_state.uploaded_image is not None and st.session_state.plant_agent:
        if st.button("Analyze Plant", type="primary"):
            with st.spinner("Analyzing your plant..."):
                try:
                    # Convert image to base64 for the agent
                    import base64
                    from io import BytesIO
                    
                    buffered = BytesIO()
                    st.session_state.uploaded_image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Get analysis from the agent
                    analysis = st.session_state.plant_agent.analyze_plant_image(img_str)
                    
                    if analysis.get("status") == "success":
                        st.session_state.analysis_result = {
                            "health_status": analysis.get("analysis", {}).get("health_status", "Unknown"),
                            "plant_type": analysis.get("analysis", {}).get("plant_type", "Unknown"),
                            "confidence": analysis.get("analysis", {}).get("confidence", 0.0),
                            "issues": analysis.get("analysis", {}).get("issues", []),
                            "care_advice": analysis.get("analysis", {}).get("recommendations", []),
                            "visual_analysis": analysis.get("visual_analysis")
                        }
                    else:
                        st.error(f"Analysis failed: {analysis.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"Error during plant analysis: {str(e)}")
                    st.session_state.analysis_result = None
        
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            st.subheader("Analysis Results")
            
            # Health status with color coding
            health_color = "green" if result["health_status"].lower() == "good" else "red"
            st.markdown(f"**Health Status:** :{health_color}[{result['health_status']}]")
            
            st.markdown(f"**Plant Type:** {result['plant_type']}")
            st.markdown(f"**Confidence:** {result['confidence']*100:.1f}%")
            
            if result.get("issues"):
                st.subheader("Potential Issues")
                for issue in result["issues"]:
                    st.markdown(f"- ❗ {issue}")
            
            st.subheader("Care Recommendations")
            for advice in result["care_advice"]:
                st.markdown(f"- 🌱 {advice}")
            
            # Show detailed AI analysis if available
            if "ai_analysis" in result:
                with st.expander("🔍 Detailed AI Analysis"):
                    st.markdown(result["ai_analysis"])
    else:
        st.info("Upload a plant photo to get started")

# Add footer
st.markdown("---")
st.markdown("### About")
st.markdown("""
This Smart Plant Care Assistant uses AI to analyze your plants and provide 
personalized care recommendations. For best results, take clear, well-lit 
photos of your plants against a neutral background.
""")

# Add some custom CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)
