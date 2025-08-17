"""
Comprehensive PlantCareAgent with full functionality including:
- Image analysis
- Chat interface
- Plant care recommendations
- Disease detection
- Growth monitoring
"""
from typing import Dict, List, Optional, Any, TypedDict, Annotated, Sequence, Union
import json
import re
from datetime import datetime
import base64
import numpy as np
from PIL import Image
import io
import cv2

# LangChain imports
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.tools.render import render_text_description
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.agents import AgentFinish, AgentAction, AgentActionMessageLog
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage, FunctionMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.agents import AgentAction, AgentFinish, AgentActionMessageLog
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from pydantic import BaseModel, Field

# Local imports
from plant_analysis import PlantImageAnalyzer

# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda a, b: a + b]
    sender: str
    plant_data: Optional[Dict[str, Any]]
    analysis_results: Optional[Dict[str, Any]]
    next: str

class PlantCareAgent:
    """Comprehensive Plant Care Agent with image analysis and chat capabilities."""
    
    def __init__(self, model_name: str = "llama3"):
        """Initialize the PlantCareAgent.
        
        Args:
            model_name: Name of the Ollama model to use (default: llama3)
        """
        self.model_name = model_name
        self.llm = self._initialize_llm()
        self.analyzer = PlantImageAnalyzer()
        self.tools = self._setup_tools()
        self.memory = self._setup_memory()
        self.workflow = self._setup_workflow()
    
    def _initialize_llm(self):
        """Initialize the language model with streaming support."""
        return ChatOllama(
            model=self.model_name,
            temperature=0.7,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
    
    def _setup_tools(self) -> List[Tool]:
        """Set up the tools available to the agent."""
        @tool
        def analyze_plant_image(image_data: str) -> Dict[str, Any]:
            """Analyze a plant image and return health assessment.
            
            Args:
                image_data: Base64 encoded image string
                
            Returns:
                Dict containing analysis results
            """
            try:
                # Check if image_data is already bytes or needs to be decoded
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
                
                return {
                    'status': 'success',
                    'health_analysis': health_analysis,
                    'disease_analysis': disease_analysis,
                    'summary': summary,
                    'message': 'Image analyzed successfully.'
                }
            except Exception as e:
                import traceback
                return {
                    'status': 'error',
                    'message': f'Error analyzing image: {str(e)}\n{traceback.format_exc()}'
                }
        
        @tool
        def get_care_instructions(plant_type: str) -> str:
            """Get care instructions for a specific plant type.
            
            Args:
                plant_type: Name of the plant species
                
            Returns:
                String with care instructions
            """
            # This is a simplified version - in a real app, this would query a database
            care_guides = {
                "rose": """Roses need full sun (at least 6 hours daily) and regular watering. 
                Water deeply 2-3 times per week. Prune in early spring before new growth begins. 
                Fertilize every 4-6 weeks during growing season. Watch for black spot and aphids.""",
                
                "orchid": """Orchids prefer bright, indirect light. Water once a week by soaking the pot for 
                15 minutes, then drain completely. Maintain humidity around 40-70%. 
                Repot every 1-2 years with orchid bark mix.""",
                
                "cactus": """Cacti need at least 6 hours of direct sunlight daily. Water every 2-3 weeks in summer, 
                once a month in winter. Use well-draining soil. Protect from temperatures below 50°F (10°C).""",
                
                "succulent": """Succulents need bright light and infrequent watering. Water only when soil is completely dry, 
                then soak thoroughly. Use well-draining soil. Protect from frost.""",
                
                "basil": """Basil needs 6-8 hours of sunlight daily. Keep soil consistently moist but not waterlogged. 
                Pinch off flower buds to encourage leaf growth. Harvest leaves regularly to promote bushiness."""
            }
            
            plant_type = plant_type.lower()
            return care_guides.get(
                plant_type, 
                f"General care: Provide bright, indirect light and water when the top inch of soil is dry. "
                f"Ensure good drainage and protect from extreme temperatures."
            )
        
        @tool
        def identify_plant_species(image_data: str) -> Dict[str, Any]:
            """Identify a plant species from an image."""
            # In a real implementation, this would use a plant identification API
            # For now, we'll return a mock response
            return {
                "species": "Rosa",
                "common_name": "Rose",
                "confidence": 0.87,
                "description": "A flowering plant of the genus Rosa, known for its beautiful and fragrant flowers."
            }
        
        @tool
        def diagnose_plant_issues(symptoms: str, plant_type: str = None) -> str:
            """Diagnose potential plant health issues based on symptoms."""
            # This is a simplified version - in a real app, this would use more sophisticated logic
            symptoms = symptoms.lower()
            plant_type = plant_type.lower() if plant_type else "plant"
            
            issues = []
            
            # Check for common issues
            if "yellow" in symptoms and "leaf" in symptoms:
                if "bottom" in symptoms:
                    issues.append("Overwatering or nitrogen deficiency")
                else:
                    issues.append("Nutrient deficiency (possibly iron or magnesium)")
            
            if "brown" in symptoms and "tip" in symptoms:
                issues.append("Over-fertilization or salt buildup in soil")
            
            if "white" in symptoms and "powder" in symptoms:
                issues.append("Powdery mildew - a fungal disease")
            
            if "spots" in symptoms and "black" in symptoms:
                issues.append("Fungal infection (possibly black spot)")
            
            if not issues:
                return f"I couldn't identify specific issues. For {plant_type}, ensure proper watering, light, and check for pests regularly."
            
            return f"Possible issues for {plant_type}: " + "; ".join(issues)
        
        return [
            Tool(
                name="analyze_plant_image",
                func=analyze_plant_image,
                description="""Useful for analyzing plant health from an image. 
                Input should be a base64 encoded image string."""
            ),
            Tool(
                name="get_care_instructions",
                func=get_care_instructions,
                description="""Useful for getting care instructions for a specific plant type. 
                Input should be the name of the plant species."""
            ),
            Tool(
                name="identify_plant_species",
                func=identify_plant_species,
                description="""Useful for identifying a plant species from an image. 
                Input should be a base64 encoded image string."""
            ),
            Tool(
                name="diagnose_plant_issues",
                func=diagnose_plant_issues,
                description="""Useful for diagnosing plant health issues. 
                Input should be a description of the symptoms and optionally the plant type."""
            )
        ]
    
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
        
        # Generate recommendations
        recommendations = []
        
        # Watering recommendations
        if health_analysis.get('yellow_percentage', 0) > 30:
            recommendations.append("Check watering schedule - yellowing leaves may indicate overwatering.")
        
        # Nutrient recommendations
        if health_analysis.get('brown_percentage', 0) > 20:
            recommendations.append("Consider fertilizing - browning leaves may indicate nutrient deficiency.")
        
        # Disease recommendations
        if disease_detected:
            recommendations.append("Treat for detected diseases to prevent further spread.")
        
        # Default care tips
        if not recommendations:
            recommendations.extend([
                "Your plant looks healthy! Continue with your current care routine.",
                "Regularly check for pests and remove dead leaves.",
                "Ensure proper drainage to prevent root rot."
            ])
        
        # Create summary dictionary
        summary = {
            'health_status': f"{health_emoji} {health_status}",
            'health_score': f"{health_score:.1f}%",
            'yellow_leaves': f"{health_analysis.get('yellow_percentage', 0):.1f}%",
            'brown_leaves': f"{health_analysis.get('brown_percentage', 0):.1f}%",
            'disease_detected': disease_detected,
            'disease_warnings': disease_warnings,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
        
    def _setup_memory(self):
        """Set up conversation memory."""
        return ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,  # Keep last 5 messages
            return_messages=True,
            input_key="input",
            output_key="output"
        )
    
    def _setup_workflow(self):
        """Set up the LangGraph workflow for the agent."""
        # Define the nodes
        def agent_node(state: AgentState) -> Dict[str, Any]:
            # Prepare the prompt
            prompt = self._create_agent_prompt()
            
            # Get the agent
            agent = self._create_agent(prompt)
            
            # Run the agent
            result = agent(state)
            
            # Return the result
            return {"messages": [result["messages"][-1]]}
        
        # Define the workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Define edges
        workflow.add_edge("tools", "agent")
        
        # Define conditional edges
        def route_to_tools(state: AgentState) -> str:
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return "end"
        
        workflow.add_conditional_edges(
            "agent",
            route_to_tools,
            {
                "tools": "tools",
                "end": END
            }
        )
        
        # Set the entry point
        workflow.set_entry_point("agent")
        
        # Compile the workflow
        return workflow.compile()
    
    def _create_agent_prompt(self) -> ChatPromptTemplate:
        """Create the agent's prompt template."""
        system_message = """You are a helpful plant care assistant. Your goal is to help users take care of their plants 
        by providing accurate and helpful information about plant care, diagnosing issues, and offering recommendations.
        
        You have access to the following tools:
        {tools}
        
        Use the following format:
        
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        
        Begin!"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
        
        return prompt
    
    def _create_agent(self, prompt: ChatPromptTemplate):
        """Create the agent executor."""
        llm_with_stop = self.llm.bind(stop=["\nObservation"])
        
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
                "chat_history": lambda x: x["chat_history"]
            }
            | prompt
            | llm_with_stop
            | ReActSingleInputOutputParser()
        )
        
        return agent
    
    def chat(self, message: str, chat_history: list = None) -> str:
        """Process a chat message and return a response."""
        try:
            # Prepare the chat history
            messages = []
            
            # Add image data if provided
            if image_data:
                input_data["image_data"] = image_data
            
            # Run the workflow
            result = self.workflow.invoke(input_data)
            
            # Get the final response
            response = result["messages"][-1].content
            
            # Update memory
            self.memory.save_context(
                {"input": message},
                {"output": response}
            )
            
            return response
            
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again with a different query."
    
    def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze a plant image.
        
        Args:
            image_data: Base64 encoded image string
            
        Returns:
            Analysis results as a dictionary
        """
        return self.tools[0].func(image_data)
    
    def get_care_instructions(self, plant_type: str) -> str:
        """Get care instructions for a plant type.
        
        Args:
            plant_type: Name of the plant species
            
        Returns:
            Care instructions as a string
        """
        return self.tools[1].func(plant_type)
    
    def identify_plant(self, image_data: str) -> Dict[str, Any]:
        """Identify a plant from an image.
        
        Args:
            image_data: Base64 encoded image string
            
        Returns:
            Identification results as a dictionary
        """
        return self.tools[2].func(image_data)
    
    def diagnose_issues(self, symptoms: str, plant_type: str = None) -> str:
        """Diagnose plant health issues.
        
        Args:
            symptoms: Description of symptoms
            plant_type: Optional plant type
            
        Returns:
            Diagnosis as a string
        """
        return self.tools[3].func(symptoms, plant_type)

# For testing
if __name__ == "__main__":
    agent = PlantCareAgent()
    print("Plant Care Agent initialized successfully!")
    
    # Test chat
    print("\nTesting chat...")
    response = agent.chat("What's wrong with my rose plant? The leaves are turning yellow.")
    print(f"Response: {response}")
    
    # Test care instructions
    print("\nTesting care instructions...")
    care = agent.get_care_instructions("rose")
    print(f"Care instructions: {care}")
