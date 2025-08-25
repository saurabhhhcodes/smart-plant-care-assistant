import os
from typing import Dict, List, Optional, Any
import json
import base64
import numpy as np
from PIL import Image
import io
import cv2

# LangChain imports


from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
try:
    from langchain_together import TogetherLLM
except ImportError:
    TogetherLLM = None
try:
    from langchain_community.llms import Ollama
except ImportError:
    Ollama = None
try:
    from langchain_cohere import ChatCohere
except ImportError:
    ChatCohere = None
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None
try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None
try:
    from langchain_perplexity import ChatPerplexity
except ImportError:
    ChatPerplexity = None
try:
    from langchain_huggingface import HuggingFaceHub
except ImportError:
    HuggingFaceHub = None
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# Local imports
from plant_analysis import PlantImageAnalyzer

class PlantCareAgent:
    """Plant Care Agent that works with multiple LLM providers."""
    
    def __init__(self, api_key: str = None, provider: str = "openai"):
        """Initialize the PlantCareAgent with the specified provider.
        
        Args:
            api_key: API key for the selected provider
            provider: LLM provider ("openai", "anthropic", "together")
        """
        self.api_key = api_key
        self.provider = provider
        self.llm = self._initialize_llm()
        self.analyzer = PlantImageAnalyzer()
    
    def _initialize_llm(self):
        """Initialize the language model based on the provider."""
        if self.provider == "openai":
            return ChatOpenAI(
                model="gpt-4o",  # latest stable OpenAI model
                api_key=self.api_key,
                temperature=0.7
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                model="claude-3-opus-20240229",  # latest Claude 3 Opus
                anthropic_api_key=self.api_key,
                temperature=0.7
            )
        elif self.provider == "together":
            if TogetherLLM is not None:
                return TogetherLLM(
                    model="meta-llama/Llama-3-70b-chat-hf",  # Llama 3 70B
                    together_api_key=self.api_key,
                    temperature=0.7
                )
            else:
                raise ImportError("TogetherLLM is not available in this version of langchain_together. Please update your requirements or code.")
        elif self.provider == "ollama":
            if Ollama is not None:
                return Ollama(model="llama3", temperature=0.7)  # Llama 3 is latest in Ollama
            else:
                raise ImportError("Ollama is not available. Please install langchain_community and run an Ollama server.")
        elif self.provider == "cohere":
            if ChatCohere is not None:
                return ChatCohere(
                    model="command-r-plus",  # latest Cohere command model
                    cohere_api_key=self.api_key,
                    temperature=0.7
                )
            else:
                raise ImportError("ChatCohere is not available. Please install langchain_cohere.")
        elif self.provider == "gemini":
            if ChatGoogleGenerativeAI is not None:
                return ChatGoogleGenerativeAI(
                    model="models/gemini-1.5-pro-latest",  # latest Gemini model as of 2025
                    google_api_key=self.api_key,
                    temperature=0.7
                )
            else:
                raise ImportError("ChatGoogleGenerativeAI is not available. Please install langchain_google_genai.")
        elif self.provider == "mistral":
            if ChatMistralAI is not None:
                return ChatMistralAI(
                    model="mistral-large-latest",  # latest Mistral model
                    mistral_api_key=self.api_key,
                    temperature=0.7
                )
            else:
                raise ImportError("ChatMistralAI is not available. Please install langchain_mistralai.")
        elif self.provider == "perplexity":
            if ChatPerplexity is not None:
                return ChatPerplexity(
                    model="pplx-70b-online",  # latest Perplexity model
                    perplexity_api_key=self.api_key,
                    temperature=0.7
                )
            else:
                raise ImportError("ChatPerplexity is not available. Please install langchain_perplexity.")
        elif self.provider == "huggingface":
            if HuggingFaceHub is not None:
                return HuggingFaceHub(
                    repo_id="HuggingFaceH4/zephyr-7b-beta",  # Zephyr 7B Beta is a strong open model
                    huggingfacehub_api_token=self.api_key
                )
            else:
                raise ImportError("HuggingFaceHub is not available. Please install langchain_huggingface.")
        else:
            # Default to OpenAI if no provider specified
            return ChatOpenAI(
                model="gpt-4o",
                api_key=self.api_key,
                temperature=0.7
            )
    
    def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze a plant image and return health assessment.
        
        Args:
            image_data: Base64 encoded image string
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Decode base64 image
            if isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    # Handle data URL format
                    img_str = image_data.split(',')[1]
                    img_bytes = base64.b64decode(img_str)
                else:
                    # Assume it's a base64 string
                    img_bytes = base64.b64decode(image_data)
            else:
                img_bytes = image_data
                
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is None:
                return {
                    'status': 'error',
                    'message': 'Failed to decode image. Please try again with a different image.'
                }
            
            # Analyze the image
            health_analysis = self.analyzer.analyze_plant_health(img)
            disease_analysis = self.analyzer.detect_diseases(img)
            
            # Generate a summary of the analysis
            summary = self._generate_analysis_summary(health_analysis, disease_analysis)
            
            # Generate care recommendations using LLM
            recommendations = self._generate_care_recommendations(health_analysis, disease_analysis)
            
            return {
                'status': 'success',
                'health_analysis': health_analysis,
                'disease_analysis': disease_analysis,
                'summary': summary,
                'recommendations': recommendations,
                'message': 'Image analyzed successfully.'
            }
        except Exception as e:
            import traceback
            return {
                'status': 'error',
                'message': f'Error analyzing image: {str(e)}\n{traceback.format_exc()}'
            }
    
    def _generate_analysis_summary(self, health_analysis: Dict, disease_analysis: Dict) -> Dict:
        """Generate a summary of the plant health analysis.
        
        Args:
            health_analysis: Dictionary containing health metrics
            disease_analysis: Dictionary containing disease metrics
            
        Returns:
            Dictionary with analysis summary
        """
        # Determine overall health status
        health_score = health_analysis.get('healthy_percentage', 0)
        
        if health_score > 70:
            health_status = "Healthy"
            health_emoji = "🟢"
        elif health_score > 40:
            health_status = "Moderately Healthy"
            health_emoji = "🟡"
        else:
            health_status = "Unhealthy"
            health_emoji = "🔴"
        
        # Check for disease indicators
        disease_detected = False
        disease_warnings = []
        
        for disease, percentage in disease_analysis.items():
            if percentage > 10:  # Threshold for considering it significant
                disease_detected = True
                disease_name = disease.replace('_', ' ').title()
                disease_warnings.append(f"{disease_name}: {percentage:.1f}%")
        
        # Create summary dictionary
        summary = {
            'health_status': f"{health_emoji} {health_status}",
            'health_score': f"{health_score:.1f}%",
            'yellow_leaves': f"{health_analysis.get('yellow_percentage', 0):.1f}%",
            'brown_leaves': f"{health_analysis.get('brown_percentage', 0):.1f}%",
            'disease_detected': disease_detected,
            'disease_warnings': disease_warnings,
            'timestamp': self._get_current_timestamp()
        }
        
        return summary
    
    def _generate_care_recommendations(self, health_analysis: Dict, disease_analysis: Dict) -> List[str]:
        """Generate care recommendations using the LLM.
        
        Args:
            health_analysis: Dictionary containing health metrics
            disease_analysis: Dictionary containing disease metrics
            
        Returns:
            List of care recommendations
        """
        # Create a prompt for the LLM
        prompt = f"""
        Based on the following plant health analysis, provide 3-5 specific care recommendations:
        
        Health Analysis:
        - Healthy percentage: {health_analysis.get('healthy_percentage', 0):.1f}%
        - Yellowing percentage: {health_analysis.get('yellow_percentage', 0):.1f}%
        - Browning percentage: {health_analysis.get('brown_percentage', 0):.1f}%
        
        Disease Analysis:
        {disease_analysis}
        
        Please provide actionable recommendations that address the specific issues detected.
        Focus on watering, lighting, fertilizing, and any disease treatment if needed.
        """
        
        try:
            # Get recommendations from the LLM
            response = self.llm.invoke(prompt)
            recommendations = response.content.strip().split('\n')
            # Filter out empty lines and return as list
            return [rec.strip() for rec in recommendations if rec.strip()]
        except Exception as e:
            # Fallback to default recommendations if LLM fails
            return self._get_default_recommendations(health_analysis, disease_analysis)
    
    def _get_default_recommendations(self, health_analysis: Dict, disease_analysis: Dict) -> List[str]:
        """Get default care recommendations when LLM is not available.
        
        Args:
            health_analysis: Dictionary containing health metrics
            disease_analysis: Dictionary containing disease metrics
            
        Returns:
            List of care recommendations
        """
        recommendations = []
        
        # Watering recommendations
        if health_analysis.get('yellow_percentage', 0) > 30:
            recommendations.append("Check watering schedule - yellowing leaves may indicate overwatering.")
        
        # Nutrient recommendations
        if health_analysis.get('brown_percentage', 0) > 20:
            recommendations.append("Consider fertilizing - browning leaves may indicate nutrient deficiency.")
        
        # Disease recommendations
        disease_detected = any(percentage > 10 for key, percentage in disease_analysis.items() if key.endswith('_percentage'))
        if disease_detected:
            recommendations.append("Treat for detected diseases to prevent further spread.")
        
        # Default care tips
        if not recommendations:
            recommendations.extend([
                "Your plant looks healthy! Continue with your current care routine.",
                "Regularly check for pests and remove dead leaves.",
                "Ensure proper drainage to prevent root rot."
            ])
        
        return recommendations
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def chat(self, message: str, chat_history: list = None) -> str:
        """Process a chat message and return a response, always forcing UTF-8 encoding for output."""
        try:
            messages = []
            messages.append(SystemMessage(content="""
            You are a helpful plant care assistant. Your goal is to help users take care of their plants 
            by providing accurate and helpful information about plant care, diagnosing issues, and offering recommendations.
            When users ask about plant care, consider:
            - Watering needs (frequency, amount, technique)
            - Light requirements (direct, indirect, low, high)
            - Soil and drainage preferences
            - Fertilization schedules
            - Common problems and solutions
            - Seasonal care adjustments
            - Pest identification and treatment
            - Disease prevention and treatment
            Always provide specific, actionable advice based on the plant type if mentioned.
            """))
            if chat_history:
                for msg in chat_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    else:
                        messages.append(SystemMessage(content=msg["content"]))
            messages.append(HumanMessage(content=message))
            response = self.llm.invoke(messages)
            # Force UTF-8 encoding/decoding at every step
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = response
            if isinstance(content, bytes):
                return content.decode('utf-8', errors='replace')
            # If it's a string, re-encode and decode to force UTF-8
            return str(content).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again with a different query."
    
    def get_care_instructions(self, plant_type: str) -> str:
        """Get care instructions for a specific plant type.
        
        Args:
            plant_type: Name of the plant species
            
        Returns:
            Care instructions as a string
        """
        # Create a prompt for the LLM
        prompt = f"""
        Provide care instructions for a {plant_type} plant. Include information about:
        - Watering needs
        - Light requirements
        - Soil preferences
        - Temperature and humidity preferences
        - Fertilization schedule
        - Common problems and solutions
        
        Format the response as a clear, structured guide.
        """
        
        try:
            # Get response from the LLM
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating care instructions: {str(e)}"

# For testing
if __name__ == "__main__":
    # This is just for testing purposes
    agent = PlantCareAgent()
    print("Plant Care Agent initialized successfully!")