

import streamlit as st
import sys
import io
import os
import locale
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
import base64
from datetime import datetime

# Ensure UTF-8 encoding for all output (fixes emoji errors)
try:
    if sys.getdefaultencoding().lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Try to set locale to UTF-8
    locale.setlocale(locale.LC_ALL, '')
    if locale.getpreferredencoding().lower() != 'utf-8':
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    # Set PYTHONIOENCODING for subprocesses
    os.environ['PYTHONIOENCODING'] = 'utf-8'
except Exception as e:
    st.warning(f"Could not set UTF-8 encoding: {e}")

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
        provider_display = st.selectbox(
            "Select Provider",
            [
                "openai",
                "anthropic",
                "together",
                "cohere",
                "gemini",
                "mistral",
                "perplexity",
                "huggingface",
                "ollama (open source LLMs)",
                "local-hf (TinyLlama, open source, no API key)",
            ],
            index=0,
            help="Select the LLM provider to use for analysis. 'local-hf' runs a small open source model (TinyLlama) directly on your machine, no API key required."
        )
        # Normalize provider value for backend
        if provider_display.startswith("ollama"):
            provider = "ollama"
        elif provider_display.startswith("local-hf"):
            provider = "local-hf"
        else:
            provider = provider_display
        st.session_state.provider = provider

        # API key input (completely hide for open source providers)
        if provider in ["ollama", "local-hf"]:
            api_key = ""
            if provider == "ollama":
                st.info("Ollama does not require an API key if running locally.")
            elif provider == "local-hf":
                st.info("'local-hf' runs TinyLlama (open source) directly on your machine. No API key needed, but requires sufficient RAM and CPU/GPU.")
                # Check for transformers/torch at runtime and show a user-friendly error if missing
                try:
                    import transformers, torch
                except ImportError:
                    st.error("❌ Required packages 'transformers' and 'torch' are not installed. Please install them with:\n\n    pip install transformers torch\n\nThen restart the app.")
                    return
        else:
            provider_label = {
                "openai": "OpenAI",
                "anthropic": "Anthropic",
                "together": "Together.ai",
                "cohere": "Cohere",
                "gemini": "Google Gemini",
                "mistral": "Mistral AI",
                "perplexity": "Perplexity AI",
                "huggingface": "Hugging Face Hub",
            }.get(provider, provider.title())
            st.subheader(f"API Key for {provider_label}")
            api_key = st.text_input(
                f"Enter your {provider_label} API key",
                type="password",
                help=f"Enter your {provider_label} API key",
                value=st.session_state.api_key
            )
        st.session_state.api_key = api_key

        # Auto-initialize for open source providers
        if provider in ["ollama", "local-hf"] and not st.session_state.agent_initialized:
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
        # Manual initialize for API-key providers
        elif provider not in ["ollama", "local-hf"]:
            button_disabled = not bool(api_key)
            if st.button("Initialize Agent", disabled=button_disabled):
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

        # Status indicators
        st.subheader("Status")
        if st.session_state.agent_initialized:
            st.success("✅ Plant Care Agent is ready")
        else:
            st.error("❌ Plant Care Agent not initialized")
            # Only show API key warning for providers that require it
            if provider not in ["ollama", "local-hf"]:
                st.info("Please enter your API key and click 'Initialize Agent'")
            else:
                st.info("Click 'Initialize Agent' to start using the open source LLM provider.")

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
    
    # File uploader for images
    uploaded_file = st.file_uploader(
        "Upload a photo of your plant",
        type=["jpg", "jpeg", "png"],
        key="file_uploader"
    )

    # Video uploader
    uploaded_video = st.file_uploader(
        "Or upload a video of your plant (analyzes first frame)",
        type=["mp4", "mov", "avi"],
        key="video_uploader"
    )

    # Camera input (Streamlit native)
    camera_image = st.camera_input("Or take a photo with your camera")

    # Prefer video > camera > image
    image_to_use = None
    video_to_use = None
    if uploaded_video is not None:
        # Save video to a temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
            tmp_vid.write(uploaded_video.read())
            video_path = tmp_vid.name
        st.session_state.uploaded_video_path = video_path
        st.video(video_path)
        video_to_use = video_path
    elif camera_image is not None:
        try:
            image = Image.open(camera_image)
            st.image(image, caption="Camera Plant Image", use_container_width=True)
            st.session_state.uploaded_image = image
            image_to_use = image
        except Exception as e:
            st.error(f"Error loading camera image: {str(e)}")
            return
    elif uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Plant Image", use_container_width=True)
            st.session_state.uploaded_image = image
            image_to_use = image
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            return

    # Analysis button
    if st.button("Analyze Plant", disabled=not st.session_state.agent_initialized or (image_to_use is None and video_to_use is None)):
        if video_to_use is not None:
            analyze_plant_video(video_to_use)
        else:
            analyze_plant_image()

def analyze_plant_video(video_path):
    """Analyze the first frame of the uploaded plant video."""
    if not video_path:
        st.warning("Please upload a video first")
        return
    with st.spinner("Analyzing your plant video..."):
        try:
            if st.session_state.agent_initialized and st.session_state.plant_agent:
                analysis = st.session_state.plant_agent.analyzer.analyze_video(video_path)
                if analysis.get('status') == 'error':
                    st.error(analysis.get('message', 'Unknown error'))
                else:
                    st.success("Video analysis complete! 🎉 (First frame)")
                    st.json(analysis)
            else:
                st.error("Plant Care Agent is not initialized")
        except Exception as e:
            st.error(f"Error during video analysis: {str(e)}")

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
    try:
        if analysis.get('status') == 'success':
            st.success("Analysis complete! 🎉")
            
            # Display species
            if 'species' in analysis:
                st.subheader("🌿 Plant Species")
                st.write(analysis['species'])

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
                    rec_text = rec.strip()
                    if rec_text.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.')):
                        rec_text = rec_text[1:].strip()
                    # Force UTF-8 for display
                    st.info(f"• {rec_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')}")
        else:
            st.error(f"Analysis failed: {analysis.get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Unicode error displaying analysis: {str(e)}")

def display_chat_interface():
    """Display the chat interface for plant care questions."""
    st.header("💬 Chat with Plant Expert")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            try:
                # Always force UTF-8 for display
                content = message["content"]
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='replace')
                else:
                    content = str(content).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                st.markdown(content)
            except Exception as e:
                st.markdown(f"[Unicode error displaying message: {e}]")

    # Chat input
    prompt = st.chat_input("Ask me anything about plant care...", disabled=not st.session_state.agent_initialized)
    if prompt is not None:
        try:
            # Force UTF-8 for input
            if isinstance(prompt, bytes):
                prompt = prompt.decode('utf-8', errors='replace')
            else:
                prompt = str(prompt).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception:
            pass
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
                        # Always force UTF-8 for output
                        if isinstance(response, bytes):
                            response = response.decode('utf-8', errors='replace')
                        else:
                            response = str(response).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
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