import streamlit as st
import os
import sys
from pathlib import Path
from PIL import Image
import io
import cv2
import numpy as np
import base64
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the plant agent
try:
    from plant_agent import PlantCareAgent
except ImportError as e:
    st.error(f"Failed to import PlantCareAgent: {e}")
    st.error("Please make sure all dependencies are installed and the file exists.")
    st.stop()

def initialize_session_state():
    """Initialize session state variables."""
    if 'plant_agent' not in st.session_state:
        st.session_state.plant_agent = None
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'provider' not in st.session_state:
        st.session_state.provider = "openai"
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Plant Care Assistant. How can I help you with your plants today?"}
        ]

def display_sidebar():
    """Display the sidebar with LLM provider selection and API key input."""
    with st.sidebar:
        st.title("🌱 Plant Care Assistant")
        
        # Provider selection
        st.subheader("LLM Provider")
        provider = st.selectbox(
            "Select Provider",
            ["openai", "anthropic", "together"],
            index=0,
            help="Select the LLM provider to use for analysis"
        )
        st.session_state.provider = provider
        
        # API key input
        st.subheader("API Key")
        api_key = st.text_input(
            "Enter your API key",
            type="password",
            help=f"Enter your {provider.title()} API key",
            value=st.session_state.api_key
        )
        st.session_state.api_key = api_key
        
        # Initialize button
        if st.button("Initialize Agent"):
            if api_key:
                try:
                    with st.spinner("Initializing Plant Care Agent..."):
                        st.session_state.plant_agent = PlantCareAgent(
                            api_key=api_key,
                            provider=provider
                        )
                        st.session_state.agent_initialized = True
                        st.success("✅ Plant Care Agent initialized successfully!")
                except Exception as e:
                    st.error(f"Error initializing Plant Care Agent: {str(e)}")
                    st.session_state.agent_initialized = False
            else:
                st.warning("Please enter your API key")
        
        # Status indicators
        st.subheader("Status")
        if st.session_state.agent_initialized:
            st.success("✅ Plant Care Agent is ready")
        else:
            st.error("❌ Plant Care Agent not initialized")
            st.info("Please enter your API key and click 'Initialize Agent'")
        
        # App information
        st.subheader("About")
        st.info("""
        This app uses real LLMs to analyze plant health and provide care recommendations.
        
        **Features:**
        - 📸 Upload plant photos for analysis
        - 💬 Chat with the plant care assistant
        - 🌿 Get personalized care tips
        - 🔍 Identify plant health issues
        """)

def display_upload_section():
    """Display the image upload and analysis section."""
    st.header("🌿 Plant Analysis")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a photo of your plant",
        type=["jpg", "jpeg", "png"],
        key="file_uploader"
    )
    
    # Display uploaded image
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Plant Image", use_column_width=True)
            st.session_state.uploaded_image = image
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            return
    
    # Analysis button
    if st.button("Analyze Plant", disabled=not st.session_state.agent_initialized or 'uploaded_image' not in st.session_state):
        analyze_plant_image()

def analyze_plant_image():
    """Analyze the uploaded plant image."""
    if 'uploaded_image' not in st.session_state:
        st.warning("Please upload an image first")
        return
    
    with st.spinner("Analyzing your plant..."):
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            st.session_state.uploaded_image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Get analysis from the agent
            if st.session_state.agent_initialized and st.session_state.plant_agent:
                analysis = st.session_state.plant_agent.analyze_image(img_str)
                display_analysis_results(analysis)
            else:
                st.error("Plant Care Agent is not initialized")
                
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")

def display_analysis_results(analysis):
    """Display the analysis results in a user-friendly format."""
    if analysis.get('status') == 'success':
        st.success("Analysis complete! 🎉")
        
        # Display health metrics
        health = analysis.get('health_analysis', {})
        st.subheader("🌱 Plant Health Summary")
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Health Score", f"{health.get('healthy_percentage', 0):.1f}%")
        with col2:
            st.metric("Yellowing", f"{health.get('yellow_percentage', 0):.1f}%")
        with col3:
            st.metric("Browning", f"{health.get('brown_percentage', 0):.1f}%")
        
        # Display care recommendations
        if 'recommendations' in analysis:
            st.subheader("💡 Care Recommendations")
            for rec in analysis['recommendations']:
                # Remove any bullet points or numbering that might be in the recommendations
                rec_text = rec.strip()
                if rec_text.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.')):
                    rec_text = rec_text[1:].strip()
                st.info(f"• {rec_text}")
                
    else:
        st.error(f"Analysis failed: {analysis.get('message', 'Unknown error')}")

def display_chat_interface():
    """Display the chat interface for plant care questions."""
    st.header("💬 Chat with Plant Expert")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about plant care...", disabled=not st.session_state.agent_initialized):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if st.session_state.agent_initialized and st.session_state.plant_agent:
                        response = st.session_state.plant_agent.chat(
                            message=prompt,
                            chat_history=st.session_state.messages[:-1]
                        )
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        st.error("Plant Care Agent is not initialized")
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    # Set page config
    st.set_page_config(
        page_title="🌱 Smart Plant Care Assistant",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Main content
    st.title("🌱 Smart Plant Care Assistant")
    st.markdown("### 🌿 AI-Powered Plant Health Analysis with Real LLMs")
    
    # Create tabs for different features
    tab1, tab2 = st.tabs(["📸 Analyze Plant", "💬 Chat with Expert"])
    
    with tab1:
        display_upload_section()
    
    with tab2:
        display_chat_interface()

if __name__ == "__main__":
    main()