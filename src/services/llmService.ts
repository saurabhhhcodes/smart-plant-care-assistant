// Initialize Ollama client (using fetch API instead of node modules)
const OLLAMA_HOST = 'http://localhost:11434';

// Simple Ollama client using fetch
const ollamaClient = {
  async list() {
    const response = await fetch(`${OLLAMA_HOST}/api/tags`);
    if (!response.ok) throw new Error('Ollama not available');
    return response.json();
  },
  
  async chat(params: { model: string; messages: any[]; options?: any }) {
    const response = await fetch(`${OLLAMA_HOST}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!response.ok) throw new Error('Ollama chat failed');
    return response.json();
  }
};

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

export class LLMService {
  private static instance: LLMService;
  private isOllamaAvailable: boolean = false;

  private constructor() {
    this.checkOllamaAvailability();
  }

  public static getInstance(): LLMService {
    if (!LLMService.instance) {
      LLMService.instance = new LLMService();
    }
    return LLMService.instance;
  }

  private async checkOllamaAvailability(): Promise<void> {
    try {
      await ollamaClient.list();
      this.isOllamaAvailable = true;
      console.log('Ollama is available');
    } catch (error) {
      console.warn('Ollama not available, using fallback responses');
      this.isOllamaAvailable = false;
    }
  }

  public async generatePlantAdvice(analysis: PlantAnalysis): Promise<AIAdvice> {
    if (!this.isOllamaAvailable) {
      return this.generateFallbackAdvice(analysis);
    }

    try {
      const prompt = this.buildPlantCarePrompt(analysis);
      
      const response = await ollamaClient.chat({
        model: 'llama3.2', // or any other model you have installed
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        options: {
          temperature: 0.7,
          top_p: 0.9,
        }
      });

      return this.parseLLMResponse(response.message.content);
    } catch (error) {
      console.error('Error generating advice with Ollama:', error);
      return this.generateFallbackAdvice(analysis);
    }
  }

  private buildPlantCarePrompt(analysis: PlantAnalysis): string {
    return `You are an expert plant care assistant. Based on the following plant analysis, provide helpful advice:

Plant Health: ${analysis.health}
Watering Status: ${analysis.watering}
Light Conditions: ${analysis.light}
Issues Detected: ${analysis.issues.join(', ') || 'None'}
Confidence: ${analysis.confidence}%

Please provide advice in the following JSON format:
{
  "summary": "Brief summary of plant condition",
  "recommendations": ["action item 1", "action item 2", "action item 3"],
  "wateringSchedule": "Specific watering advice",
  "careTips": ["tip 1", "tip 2", "tip 3", "tip 4"]
}

Focus on practical, actionable advice that a plant owner can implement immediately.`;
  }

  private parseLLMResponse(response: string): AIAdvice {
    try {
      // Try to extract JSON from the response
      const startIndex = response.indexOf('{');
      const endIndex = response.lastIndexOf('}');
      if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
        const jsonStr = response.substring(startIndex, endIndex + 1);
        const parsed = JSON.parse(jsonStr);
        return {
          summary: parsed.summary || 'Plant analysis complete',
          recommendations: parsed.recommendations || [],
          wateringSchedule: parsed.wateringSchedule || 'Follow general care guidelines',
          careTips: parsed.careTips || []
        };
      }
    } catch (error) {
      console.error('Error parsing LLM response:', error);
    }

    // Fallback parsing for non-JSON responses
    return this.parseTextResponse(response);
  }

  private parseTextResponse(response: string): AIAdvice {
    const lines = response.split('\n').filter(line => line.trim());
    
    return {
      summary: lines[0] || 'Plant analysis complete',
      recommendations: lines
        .filter(line => line.includes('•') || line.includes('-'))
        .map(line => line.replace(/^[•-]\s*/, ''))
        .slice(0, 4),
      wateringSchedule: 'Follow general care guidelines',
      careTips: [
        'Use room temperature water',
        'Ensure proper drainage',
        'Avoid overwatering',
        'Monitor for pests regularly'
      ]
    };
  }

  private generateFallbackAdvice(analysis: PlantAnalysis): AIAdvice {
    const healthAdvice = {
      excellent: 'Your plant is thriving! Keep up the excellent care.',
      good: 'Your plant is doing well. Continue with current care routine.',
      fair: 'Your plant needs some attention. Consider the recommendations below.',
      poor: 'Your plant needs immediate care. Follow the recommendations carefully.'
    };

    const wateringAdvice = {
      needed: 'Water your plant within the next 24 hours',
      adequate: 'Current watering schedule is appropriate',
      excessive: 'Reduce watering frequency to prevent root rot'
    };

    const lightAdvice = {
      sufficient: 'Light conditions are good for this plant',
      insufficient: 'Move plant to a brighter location',
      excessive: 'Move plant to a location with indirect light'
    };

    return {
      summary: `${healthAdvice[analysis.health]} ${wateringAdvice[analysis.watering]}. ${lightAdvice[analysis.light]}.`,
      recommendations: [
        wateringAdvice[analysis.watering],
        lightAdvice[analysis.light],
        'Check soil moisture before watering',
        'Rotate plant weekly for even growth'
      ],
      wateringSchedule: analysis.watering === 'needed' 
        ? 'Water now, then every 3-4 days' 
        : analysis.watering === 'excessive'
        ? 'Wait 1-2 weeks before next watering'
        : 'Continue current schedule',
      careTips: [
        'Use room temperature water',
        'Ensure proper drainage',
        'Avoid overwatering',
        'Monitor for pests regularly'
      ]
    };
  }

  public async getAvailableModels(): Promise<string[]> {
    try {
      const models = await ollamaClient.list();
      return models.models.map((model: any) => model.name);
    } catch (error) {
      console.error('Error fetching models:', error);
      return [];
    }
  }

  public isAvailable(): boolean {
    return this.isOllamaAvailable;
  }
}

export default LLMService.getInstance();
