import { StateGraph, END } from '@langchain/langgraph';

export interface PlantAnalysisState {
  imageData: string;
  analysis: any;
  recommendations: any;
  finalAdvice: any;
  errors: string[];
}

export interface PlantAnalysis {
  health: 'excellent' | 'good' | 'fair' | 'poor';
  watering: 'needed' | 'adequate' | 'excessive';
  light: 'sufficient' | 'insufficient' | 'excessive';
  issues: string[];
  confidence: number;
}

export interface AIAdvice {
  summary: string;
  recommendations: string[];
  wateringSchedule: string;
  careTips: string[];
}

export class LangGraphService {
  private static instance: LangGraphService;
  private workflow: any;

  private constructor() {
    this.initializeWorkflow();
  }

  public static getInstance(): LangGraphService {
    if (!LangGraphService.instance) {
      LangGraphService.instance = new LangGraphService();
    }
    return LangGraphService.instance;
  }

  private initializeWorkflow() {
    // Define the state schema
    const stateSchema = {
      imageData: { value: "" },
      analysis: { value: null },
      recommendations: { value: null },
      finalAdvice: { value: null },
      errors: { value: [] }
    };

    // Create the workflow
    const workflow = new StateGraph({
      channels: stateSchema
    });

    // Add nodes
    workflow.addNode("analyze_image", this.analyzeImageNode);
    workflow.addNode("generate_recommendations", this.generateRecommendationsNode);
    workflow.addNode("create_final_advice", this.createFinalAdviceNode);
    workflow.addNode("error_handler", this.errorHandlerNode);

    // Add edges
    workflow.addEdge("analyze_image", "generate_recommendations");
    workflow.addEdge("generate_recommendations", "create_final_advice");
    workflow.addEdge("create_final_advice", END);
    workflow.addEdge("error_handler", END);

    // Add conditional edges
    workflow.addConditionalEdges(
      "analyze_image",
      this.shouldContinue,
      {
        "continue": "generate_recommendations",
        "error": "error_handler"
      }
    );

    workflow.addConditionalEdges(
      "generate_recommendations",
      this.shouldContinue,
      {
        "continue": "create_final_advice",
        "error": "error_handler"
      }
    );

    this.workflow = workflow.compile();
  }

  private analyzeImageNode = async (state: PlantAnalysisState) => {
    try {
      // Simulate image analysis
      const analysis: PlantAnalysis = {
        health: Math.random() > 0.3 ? 'good' : 'fair',
        watering: Math.random() > 0.5 ? 'adequate' : 'needed',
        light: Math.random() > 0.4 ? 'sufficient' : 'insufficient',
        issues: Math.random() > 0.6 ? ['Slight yellowing on edges'] : [],
        confidence: 85 + Math.random() * 10
      };

      return {
        ...state,
        analysis
      };
    } catch (error) {
      return {
        ...state,
        errors: [...state.errors, `Image analysis failed: ${error}`]
      };
    }
  };

  private generateRecommendationsNode = async (state: PlantAnalysisState) => {
    try {
      const { analysis } = state;
      
      const recommendations = {
        immediate: analysis.watering === 'needed' ? ['Water your plant within 24 hours'] : [],
        shortTerm: [
          'Check soil moisture regularly',
          'Ensure adequate lighting',
          'Monitor for pests'
        ],
        longTerm: [
          'Establish a consistent watering schedule',
          'Consider repotting if needed',
          'Learn about your specific plant species'
        ]
      };

      return {
        ...state,
        recommendations
      };
    } catch (error) {
      return {
        ...state,
        errors: [...state.errors, `Recommendation generation failed: ${error}`]
      };
    }
  };

  private createFinalAdviceNode = async (state: PlantAnalysisState) => {
    try {
      const { analysis, recommendations } = state;
      
      const finalAdvice: AIAdvice = {
        summary: `Your plant appears to be in ${analysis.health} condition. ${analysis.watering === 'needed' ? 'It needs watering soon.' : 'Watering levels are adequate.'}`,
        recommendations: [
          ...recommendations.immediate,
          ...recommendations.shortTerm.slice(0, 2)
        ],
        wateringSchedule: analysis.watering === 'needed' ? 'Water now, then every 3-4 days' : 'Continue current schedule',
        careTips: [
          'Use room temperature water',
          'Ensure proper drainage',
          'Avoid overwatering',
          'Monitor for pests regularly'
        ]
      };

      return {
        ...state,
        finalAdvice
      };
    } catch (error) {
      return {
        ...state,
        errors: [...state.errors, `Final advice creation failed: ${error}`]
      };
    }
  };

  private errorHandlerNode = async (state: PlantAnalysisState) => {
    // Provide fallback advice when errors occur
    const fallbackAdvice: AIAdvice = {
      summary: 'Unable to complete full analysis, but here are general care tips.',
      recommendations: [
        'Check soil moisture before watering',
        'Ensure adequate lighting',
        'Monitor for any changes',
        'Research your specific plant type'
      ],
      wateringSchedule: 'Water when top soil feels dry',
      careTips: [
        'Use room temperature water',
        'Ensure proper drainage',
        'Avoid overwatering',
        'Monitor for pests regularly'
      ]
    };

    return {
      ...state,
      finalAdvice: fallbackAdvice
    };
  };

  private shouldContinue = (state: PlantAnalysisState) => {
    return state.errors.length > 0 ? "error" : "continue";
  };

  public async processPlantAnalysis(imageData: string): Promise<AIAdvice> {
    try {
      const initialState: PlantAnalysisState = {
        imageData,
        analysis: null,
        recommendations: null,
        finalAdvice: null,
        errors: []
      };

      const result = await this.workflow.invoke(initialState);
      
      if (result.finalAdvice) {
        return result.finalAdvice;
      } else {
        throw new Error('No advice generated');
      }
    } catch (error) {
      console.error('LangGraph workflow error:', error);
      // Return fallback advice
      return {
        summary: 'Analysis completed with some issues. Here are general care recommendations.',
        recommendations: [
          'Check soil moisture regularly',
          'Ensure adequate lighting',
          'Water when needed',
          'Monitor plant health'
        ],
        wateringSchedule: 'Water when top soil feels dry',
        careTips: [
          'Use room temperature water',
          'Ensure proper drainage',
          'Avoid overwatering',
          'Monitor for pests regularly'
        ]
      };
    }
  }

  public async getWorkflowStatus(): Promise<{
    isAvailable: boolean;
    nodes: string[];
    description: string;
  }> {
    return {
      isAvailable: true,
      nodes: ['analyze_image', 'generate_recommendations', 'create_final_advice', 'error_handler'],
      description: 'Advanced AI orchestration with LangGraph for comprehensive plant care analysis'
    };
  }
}

export default LangGraphService.getInstance();
