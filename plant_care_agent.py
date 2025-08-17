from typing import Dict, List, Optional, Any, TypedDict, Annotated, Sequence
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description
from langchain.agents import AgentFinish, AgentAction
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, FunctionMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.agents import AgentAction, AgentFinish, AgentActionMessageLog
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from pydantic import BaseModel, Field
import json
import re
from datetime import datetime
from plant_analysis import PlantImageAnalyzer

# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda a, b: a + b]
    sender: str
    plant_data: Optional[Dict[str, Any]]
    analysis_results: Optional[Dict[str, Any]]
    next: str

class PlantCareAgent:
    def __init__(self, model_name: str = "llama3"):
        """
        Initialize the Plant Care Agent with Ollama model and tools.
        
        Args:
            model_name: Name of the Ollama model to use (default: llama3)
        """
        # Initialize the LLM with streaming support
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.2,
            num_ctx=4096,
            repeat_penalty=1.1,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
        
        # Initialize plant image analyzer
        self.image_analyzer = PlantImageAnalyzer()
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,
            return_messages=True
        )
        
        # Initialize tools
        self.tools = self._setup_tools()
        
        # Initialize the agent
        self.agent = self._create_agent()
        
        # Initialize LangGraph workflow
        self.workflow = self._create_workflow()
        
    def _setup_tools(self) -> List[Tool]:
        """Set up the tools available to the agent."""
        return [
            Tool(
                name="analyze_plant_image",
                func=self.analyze_plant_image,
                description="""Analyze a plant image to detect health issues, diseases, and growth conditions.
                Input should be a base64 encoded image string.
                Returns a detailed analysis including health score and detected issues."""
            ),
            Tool(
                name="get_care_instructions",
                func=self.get_care_instructions,
                description="""Get care instructions for a specific plant type.
                Input should be the plant type/species and any specific conditions.
                Returns detailed care instructions."""
            ),
            Tool(
                name="identify_plant_species",
                func=self.identify_plant_species,
                description="""Identify a plant species from an image or description.
                Input should be an image or detailed description of the plant.
                Returns the most likely plant species and its characteristics."""
            ),
            Tool(
                name="monitor_growth_progress",
                func=self.monitor_growth_progress,
                description="""Track and analyze plant growth over time.
                Input should be current measurements and previous data.
                Returns growth analysis and recommendations."""
            ),
            Tool(
                name="diagnose_plant_health",
                func=self.diagnose_plant_health,
                description="""Diagnose plant health issues based on symptoms.
                Input should be a description of the symptoms and plant type.
                Returns a diagnosis and recommended treatment."""
            )
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools and memory."""
        # Define the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert plant care assistant with deep knowledge of botany, 
            horticulture, and plant health management. Your goal is to help users keep their plants 
            healthy and thriving. Be friendly, informative, and precise in your advice."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for plant care analysis."""
        # Define the nodes
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_plant", self._analyze_plant_node)
        workflow.add_node("diagnose_issues", self._diagnose_issues_node)
        workflow.add_node("generate_recommendations", self._generate_recommendations_node)
        workflow.add_node("provide_advice", self._provide_advice_node)
        
        # Define the edges
        workflow.add_edge("analyze_plant", "diagnose_issues")
        workflow.add_edge("diagnose_issues", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "provide_advice")
        workflow.add_edge("provide_advice", END)
        
        # Set the entry point
        workflow.set_entry_point("analyze_plant")
        
        # Compile the workflow
        return workflow.compile()
    
    # Core tool implementations
    async def analyze_plant_image(self, image_data: str) -> Dict:
        """Analyze a plant image and return health metrics."""
        try:
            # Convert base64 to image
            import base64
            image_bytes = base64.b64decode(image_data)
            image = self.image_analyzer.bytes_to_image(image_bytes)
            
            # Analyze the image
            analysis = self.image_analyzer.get_plant_analysis_report(image)
            visual_analysis = self.image_analyzer.get_visual_analysis(image)
            
            return {
                "status": "success",
                "analysis": analysis,
                "visual_analysis": base64.b64encode(
                    self.image_analyzer.image_to_bytes(visual_analysis)
                ).decode('utf-8')
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_care_instructions(self, plant_type: str, conditions: str = "") -> str:
        """Get care instructions for a specific plant type."""
        prompt = f"""Provide detailed care instructions for a {plant_type} plant. """
        if conditions:
            prompt += f"Consider these specific conditions: {conditions}"
            
        response = await self.llm.agenerate([[{"role": "user", "content": prompt}]])
        return response.generations[0][0].text
    
    async def identify_plant_species(self, description_or_image: str) -> Dict:
        """Identify a plant species from description or image."""
        # Check if input is an image (base64)
        if description_or_image.startswith("data:image"):
            # This is a simplified version - in practice, you'd use a plant ID API
            analysis = await self.analyze_plant_image(description_or_image)
            if analysis["status"] == "success":
                prompt = f"""Based on these plant characteristics, identify the most likely plant species:
                {json.dumps(analysis['analysis'], indent=2)}
                """
                response = await self.llm.agenerate([[{"role": "user", "content": prompt}]])
                return {
                    "status": "success",
                    "species": response.generations[0][0].text.strip(),
                    "confidence": "high"
                }
        
        # If not an image or analysis failed, use the description
        prompt = f"""Identify the plant species based on this description: {description_or_image}
        Return only the most likely species name and a confidence level (high/medium/low)."""
        response = await self.llm.agenerate([[{"role": "user", "content": prompt}]])
        return {"status": "success", "species": response.generations[0][0].text.strip(), "confidence": "medium"}
    
    async def diagnose_plant_health(self, symptoms: str, plant_type: str = "") -> Dict:
        """Diagnose plant health issues based on symptoms."""
        prompt = f"""Diagnose potential health issues for a {plant_type if plant_type else 'plant'} 
        with these symptoms: {symptoms}
        
        Provide:
        1. Likely issues (with confidence levels)
        2. Probable causes
        3. Recommended treatments
        4. Prevention tips"""
        
        response = await self.llm.agenerate([[{"role": "user", "content": prompt}]])
        return {"status": "success", "diagnosis": response.generations[0][0].text}
    
    async def monitor_growth_progress(self, current_data: Dict, previous_data: Dict = None) -> Dict:
        """Track and analyze plant growth over time."""
        analysis = {
            "status": "success",
            "growth_rate": "normal",
            "health_trend": "improving",
            "recommendations": []
        }
        
        # Basic growth analysis (simplified)
        if previous_data:
            # Calculate growth rate
            if 'height' in current_data and 'height' in previous_data:
                growth_rate = (current_data['height'] - previous_data['height']) / \
                            (current_data.get('days_since_last_measurement', 1) or 1)
                analysis['growth_rate'] = "fast" if growth_rate > 1.5 else "normal" if growth_rate > 0.5 else "slow"
        
        # Generate recommendations
        recommendations = []
        if 'health_score' in current_data and current_data['health_score'] < 50:
            recommendations.append("Consider adjusting watering schedule and check for pests.")
        
        analysis['recommendations'] = recommendations
        return analysis
    
    # LangGraph node implementations
    async def _analyze_plant_node(self, state: AgentState) -> Dict:
        """Node to analyze plant data."""
        messages = state['messages']
        last_message = messages[-1]
        
        # Extract plant data from message
        plant_data = {
            'image_data': last_message.get('image_data'),
            'description': last_message.get('description', ''),
            'plant_type': last_message.get('plant_type', 'unknown')
        }
        
        # Update state
        return {"plant_data": plant_data, "next": "diagnose_issues"}
    
    async def _diagnose_issues_node(self, state: AgentState) -> Dict:
        """Node to diagnose plant health issues."""
        plant_data = state['plant_data']
        
        if plant_data.get('image_data'):
            analysis = await self.analyze_plant_image(plant_data['image_data'])
        else:
            analysis = await self.diagnose_plant_health(
                plant_data['description'],
                plant_data['plant_type']
            )
        
        return {"analysis_results": analysis, "next": "generate_recommendations"}
    
    async def _generate_recommendations_node(self, state: AgentState) -> Dict:
        """Node to generate care recommendations."""
        plant_data = state['plant_data']
        analysis = state['analysis_results']
        
        # Generate recommendations based on analysis
        recommendations = []
        if 'health_score' in analysis:
            if analysis['health_score'] < 50:
                recommendations.append("Immediate attention needed. Consider repotting and checking for root rot.")
            
            if analysis.get('yellow_percentage', 0) > 20:
                recommendations.append("Yellowing leaves detected. Check watering and nutrient levels.")
        
        if not recommendations:
            recommendations = ["Your plant appears healthy. Continue current care routine."]
        
        return {"recommendations": recommendations, "next": "provide_advice"}
    
    async def _provide_advice_node(self, state: AgentState) -> Dict:
        """Node to format and provide final advice."""
        analysis = state['analysis_results']
        recommendations = state['recommendations']
        
        # Format the response
        response = {
            "status": "success",
            "analysis": analysis,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        return {"response": response, "next": END}
    
    # Main interaction methods
    async def process_query(self, query: str, image_data: str = None) -> Dict:
        """Process a user query with optional image data."""
        try:
            # Prepare the input
            input_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": query,
                        "image_data": image_data
                    }
                ]
            }
            
            # Run the workflow
            result = await self.workflow.ainvoke(input_data)
            return result.get("response", {"status": "error", "message": "No response generated"})
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def chat(self, message: str) -> str:
        """Chat with the plant care assistant.
        
        Args:
            message: The user's message
            
        Returns:
            str: The assistant's response
        """
        try:
            response = await self.agent.ainvoke({"input": message, "chat_history": self.memory.chat_memory.messages})
            return response["output"]
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_response(self, user_input: str) -> str:
        """Get a response from the plant care agent."""
        try:
            response = self.agent.invoke({
                "input": user_input,
                "chat_history": self.memory.load_memory_variables({}).get("chat_history", [])
            })
            
            if isinstance(response, dict) and 'output' in response:
                return response['output']
            elif isinstance(response, str):
                return response
            else:
                return str(response)
                
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again with a different query."

# Example usage
if __name__ == "__main__":
    # No API key needed for local Ollama
    agent = PlantCareAgent()
    
    # Example conversation
    print("Plant Care Assistant: Hello! I'm your plant care assistant. How can I help you today?")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Plant Care Assistant: Goodbye! Take care of your plants! 🌱")
            break
            
        response = agent.chat(user_input)
        print(f"\nPlant Care Assistant: {response}")
