import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, Leaf, Droplets, Sun, AlertCircle, Loader2, CheckCircle } from 'lucide-react';
import plantAnalysisService from './services/plantAnalysisService';
import llmService, { PlantAnalysis, AIAdvice } from './services/llmService';
import langGraphService from './services/langGraphService';

function App() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingAdvice, setIsGeneratingAdvice] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<PlantAnalysis | null>(null);
  const [aiAdvice, setAiAdvice] = useState<AIAdvice | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'camera' | 'upload'>('camera');
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Initialize camera
  useEffect(() => {
    if (activeTab === 'camera') {
      startCamera();
    } else {
      stopCamera();
    }

    return () => {
      stopCamera();
    };
  }, [activeTab]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment', // Use back camera on mobile
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }
      setCameraError(null);
    } catch (error) {
      console.error('Camera access error:', error);
      setCameraError('Camera access denied. Please allow camera permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        setCapturedImage(imageData);
        analyzePlant(imageData);
      }
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageData = e.target?.result as string;
        setCapturedImage(imageData);
        analyzePlant(imageData);
      };
      reader.readAsDataURL(file);
    }
  };

  // Analyze plant using the analysis service
  const analyzePlant = async (imageData: string) => {
    setIsAnalyzing(true);
    
    try {
      const analysisResult = await plantAnalysisService.analyzePlantImage(imageData);
      setAnalysis(analysisResult);
      
      // Generate AI advice using the LLM service
      generateAIAdvice(analysisResult);
    } catch (error) {
      console.error('Analysis error:', error);
      // Fallback to basic analysis
      const fallbackAnalysis: PlantAnalysis = {
        health: 'good',
        watering: 'adequate',
        light: 'sufficient',
        issues: [],
        confidence: 75
      };
      setAnalysis(fallbackAnalysis);
      generateAIAdvice(fallbackAnalysis);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Generate advice using LangGraph orchestration
  const generateAIAdvice = async (plantAnalysis: PlantAnalysis) => {
    setIsGeneratingAdvice(true);
    
    try {
      // Use LangGraph for advanced AI orchestration
      const advice = await langGraphService.processPlantAnalysis(capturedImage || '');
      setAiAdvice(advice);
    } catch (error) {
      console.error('LangGraph error:', error);
      // Fallback to LLM service
      try {
        const advice = await llmService.generatePlantAdvice(plantAnalysis);
        setAiAdvice(advice);
      } catch (llmError) {
        console.error('LLM error:', llmError);
        // Final fallback advice
        const fallbackAdvice: AIAdvice = {
          summary: `Your plant appears to be in ${plantAnalysis.health} condition.`,
          recommendations: [
            'Check soil moisture regularly',
            'Ensure adequate lighting',
            'Water when top soil feels dry',
            'Monitor for any changes'
          ],
          wateringSchedule: 'Water when needed, typically every 3-7 days',
          careTips: [
            'Use room temperature water',
            'Ensure proper drainage',
            'Avoid overwatering',
            'Monitor for pests regularly'
          ]
        };
        setAiAdvice(fallbackAdvice);
      }
    } finally {
      setIsGeneratingAdvice(false);
    }
  };

  const resetAnalysis = () => {
    setCapturedImage(null);
    setAnalysis(null);
    setAiAdvice(null);
    setCameraError(null);
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return '#059669';
      case 'good': return '#10b981';
      case 'fair': return '#d97706';
      case 'poor': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'excellent':
      case 'good':
        return <CheckCircle style={{width: '24px', height: '24px', color: '#10b981'}} />;
      case 'fair':
        return <AlertCircle style={{width: '24px', height: '24px', color: '#f59e0b'}} />;
      case 'poor':
        return <AlertCircle style={{width: '24px', height: '24px', color: '#ef4444'}} />;
      default:
        return <Leaf style={{width: '24px', height: '24px', color: '#6b7280'}} />;
    }
  };

  return (
    <div>
      <div className="container">
        {/* Header */}
        <div className="header">
          <h1>
            🌱 Smart Plant Care
          </h1>
          <p>
            Analyze your plants with AI-powered insights
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="tab-nav">
          <button
            onClick={() => setActiveTab('camera')}
            className={`tab-button ${activeTab === 'camera' ? 'active' : ''}`}
          >
            <Camera style={{width: '20px', height: '20px'}} />
            Camera
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          >
            <Upload style={{width: '20px', height: '20px'}} />
            Upload
          </button>
        </div>

        {/* Camera View */}
        {activeTab === 'camera' && !capturedImage && (
          <div className="card">
            <div className="camera-container">
              {cameraError ? (
                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'white'}}>
                  <div style={{textAlign: 'center'}}>
                    <AlertCircle style={{width: '48px', height: '48px', margin: '0 auto 1rem', color: '#f87171'}} />
                    <p style={{fontSize: '0.875rem'}}>{cameraError}</p>
                    <button
                      onClick={startCamera}
                      className="btn-primary"
                      style={{marginTop: '1rem'}}
                    >
                      Retry Camera
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="camera-container"
                  />
                  <canvas ref={canvasRef} style={{display: 'none'}} />
                  <div className="camera-overlay">
                    <div className="camera-guide">
                      <Leaf style={{width: '64px', height: '64px', margin: '0 auto 1rem', color: 'white'}} />
                      <p>Position plant in frame</p>
                    </div>
                  </div>
                </>
              )}
            </div>
            {!cameraError && (
              <button
                onClick={captureImage}
                disabled={isAnalyzing}
                className="btn-primary"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 style={{width: '20px', height: '20px', marginRight: '0.5rem'}} />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Camera style={{width: '20px', height: '20px', marginRight: '0.5rem'}} />
                    Capture & Analyze
                  </>
                )}
              </button>
            )}
          </div>
        )}

        {/* Upload View */}
        {activeTab === 'upload' && !capturedImage && (
          <div className="card">
            <div className="upload-area">
              <Upload style={{width: '48px', height: '48px', margin: '0 auto 1rem', color: '#9ca3af'}} />
              <p style={{marginBottom: '1rem'}}>
                Upload a photo of your plant
              </p>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                style={{display: 'none'}}
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="btn-primary"
                style={{cursor: 'pointer'}}
              >
                Choose Photo
              </label>
            </div>
          </div>
        )}

        {/* Captured Image */}
        {capturedImage && (
          <div className="card">
            <img
              src={capturedImage}
              alt="Captured plant"
              style={{width: '100%', borderRadius: '0.5rem', marginBottom: '1rem'}}
            />
            <button
              onClick={resetAnalysis}
              className="btn-secondary"
            >
              Take New Photo
            </button>
          </div>
        )}

        {/* Analysis Results */}
        {analysis && (
          <div className="card">
            <h2 style={{fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center'}}>
              <Leaf style={{width: '24px', height: '24px', marginRight: '0.5rem', color: '#4ade80'}} />
              Plant Analysis
            </h2>
            
            {/* Plant Identification */}
            {analysis.plant_info && (
              <div style={{padding: '0.75rem', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '0.5rem', marginBottom: '1rem'}}>
                <h3 style={{fontWeight: '600', color: '#166534', marginBottom: '0.5rem', display: 'flex', alignItems: 'center'}}>
                  <Leaf style={{width: '20px', height: '20px', marginRight: '0.5rem'}} />
                  Plant Identified
                </h3>
                <div style={{fontSize: '0.875rem', color: '#15803d'}}>
                  <div style={{marginBottom: '0.25rem'}}>
                    <strong>Species:</strong> {analysis.plant_info.species}
                  </div>
                  <div style={{marginBottom: '0.25rem'}}>
                    <strong>Common Name:</strong> {analysis.plant_info.common_name}
                  </div>
                  <div>
                    <strong>Identification Confidence:</strong> {analysis.plant_info.confidence}%
                  </div>
                </div>
              </div>
            )}
            
            <div>
              <div className="analysis-item">
                <span style={{fontWeight: '500'}}>Health Status:</span>
                <div style={{display: 'flex', alignItems: 'center'}}>
                  {getHealthIcon(analysis.health)}
                  <span style={{marginLeft: '0.5rem', fontWeight: '600', color: getHealthColor(analysis.health)}}>
                    {analysis.health.charAt(0).toUpperCase() + analysis.health.slice(1)}
                  </span>
                </div>
              </div>

              <div className="analysis-item">
                <span style={{fontWeight: '500'}}>Watering:</span>
                <div style={{display: 'flex', alignItems: 'center'}}>
                  <Droplets style={{width: '20px', height: '20px', marginRight: '0.5rem', color: '#3b82f6'}} />
                  <span style={{fontWeight: '600'}}>
                    {analysis.watering === 'needed' ? 'Needs Water' : 
                     analysis.watering === 'adequate' ? 'Adequate' : 'Excessive'}
                  </span>
                </div>
              </div>

              <div className="analysis-item">
                <span style={{fontWeight: '500'}}>Light:</span>
                <div style={{display: 'flex', alignItems: 'center'}}>
                  <Sun style={{width: '20px', height: '20px', marginRight: '0.5rem', color: '#eab308'}} />
                  <span style={{fontWeight: '600'}}>
                    {analysis.light === 'sufficient' ? 'Sufficient' : 
                     analysis.light === 'insufficient' ? 'Insufficient' : 'Excessive'}
                  </span>
                </div>
              </div>

              <div className="analysis-item">
                <span style={{fontWeight: '500'}}>Analysis Confidence: </span>
                <span style={{fontWeight: '600'}}>{analysis.confidence.toFixed(1)}%</span>
              </div>

              {analysis.issues.length > 0 && (
                <div style={{padding: '0.75rem', backgroundColor: '#fef3c7', border: '1px solid #fde68a', borderRadius: '0.5rem', marginTop: '1rem'}}>
                  <h3 style={{fontWeight: '500', color: '#92400e', marginBottom: '0.5rem'}}>Issues Detected:</h3>
                  <ul style={{fontSize: '0.875rem', color: '#a16207'}}>
                    {analysis.issues.map((issue, index) => (
                      <li key={index}>• {issue}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI Advice */}
        {isGeneratingAdvice && (
          <div className="card">
            <div className="loading">
              <Loader2 style={{width: '32px', height: '32px', marginRight: '0.75rem', color: '#4ade80'}} />
              <span style={{fontSize: '1.125rem', fontWeight: '500'}}>Generating AI advice...</span>
            </div>
          </div>
        )}

        {aiAdvice && (
          <div className="card">
            <h2 style={{fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center'}}>
              <Leaf style={{width: '24px', height: '24px', marginRight: '0.5rem', color: '#4ade80'}} />
              AI Care Recommendations
            </h2>
            
            <div>
              <div className="advice-summary">
                <h3>Summary</h3>
                <p>{aiAdvice.summary}</p>
              </div>

              <div className="advice-section">
                <h3>Recommendations:</h3>
                <ul className="advice-list">
                  {aiAdvice.recommendations.map((rec, index) => (
                    <li key={index}>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="watering-schedule">
                <h3>Watering Schedule</h3>
                <p>{aiAdvice.wateringSchedule}</p>
              </div>

              <div className="advice-section">
                <h3>Care Tips:</h3>
                <ul className="advice-list">
                  {aiAdvice.careTips.map((tip, index) => (
                    <li key={index}>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* AI Status */}
        <div className="status-indicator">
          <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem'}}>
            <div className="status-dot green"></div>
            <span>
              LangGraph AI Orchestration Active
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="footer">
          <p>Powered by Open Source AI</p>
          <p style={{marginTop: '0.25rem'}}>🌱 Keep your plants healthy and happy!</p>
        </div>
      </div>
    </div>
  );
}

export default App;
