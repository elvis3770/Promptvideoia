import React, { useState, useRef } from 'react';
import { Upload, Image, Loader, CheckCircle, AlertCircle } from 'lucide-react';
import './FrameUploader.css';

const API_BASE = 'http://localhost:8003';

export default function FrameUploader({ onAnalysisComplete, isFirstScene = false }) {
    const [isDragging, setIsDragging] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [preview, setPreview] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            processImage(file);
        }
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            processImage(file);
        }
    };

    const processImage = (file) => {
        const reader = new FileReader();
        reader.onload = async (e) => {
            const base64Data = e.target.result;
            setPreview(base64Data);
            setError(null);
            setAnalysis(null);

            // Extract just the base64 part (remove data:image/...;base64, prefix)
            const base64Only = base64Data.split(',')[1];
            const mimeType = file.type;

            await analyzeFrame(base64Only, mimeType);
        };
        reader.readAsDataURL(file);
    };

    const analyzeFrame = async (imageData, mimeType) => {
        setIsAnalyzing(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/prompts/analyze-frame`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_data: imageData,
                    mime_type: mimeType,
                    is_first_scene: isFirstScene  // Send flag to backend
                })
            });

            const result = await response.json();

            if (result.ok) {
                setAnalysis(result.analysis);
                if (onAnalysisComplete) {
                    onAnalysisComplete(result.analysis);
                }
            } else {
                setError(result.error || 'Analysis failed');
            }
        } catch (err) {
            setError(`Error: ${err.message}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const clearImage = () => {
        setPreview(null);
        setAnalysis(null);
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="frame-uploader">
            <h4>{isFirstScene ? 'Imagen del Producto' : 'Frame Anterior (Continuidad)'}</h4>

            {!preview ? (
                <div
                    className={`upload-zone ${isDragging ? 'dragging' : ''}`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <Upload size={32} />
                    <p>{isFirstScene ? 'Arrastra la imagen del producto aqui' : 'Arrastra el ultimo frame aqui'}</p>
                    <span>o haz clic para seleccionar</span>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                    />
                </div>
            ) : (
                <div className="preview-container">
                    <img src={preview} alt="Frame preview" className="frame-preview" />
                    <button className="btn-clear" onClick={clearImage}>X</button>
                </div>
            )}

            {isAnalyzing && (
                <div className="analyzing-indicator">
                    <Loader className="spin" size={20} />
                    <span>Analizando con Gemini...</span>
                </div>
            )}

            {error && (
                <div className="error-message">
                    <AlertCircle size={16} />
                    <span>{error}</span>
                </div>
            )}

            {analysis && (
                <div className="analysis-results">
                    <div className="analysis-header">
                        <CheckCircle size={16} />
                        <span>{isFirstScene ? 'Analisis del Producto' : 'Analisis de Continuidad'}</span>
                    </div>

                    <div className="analysis-grid">
                        {analysis.subject_position && (
                            <div className="analysis-item">
                                <label>Posicion Sujeto</label>
                                <span>{analysis.subject_position}</span>
                            </div>
                        )}
                        {analysis.camera_angle && (
                            <div className="analysis-item">
                                <label>Angulo Camara</label>
                                <span>{analysis.camera_angle}</span>
                            </div>
                        )}
                        {analysis.lighting && (
                            <div className="analysis-item">
                                <label>Iluminacion</label>
                                <span>{analysis.lighting}</span>
                            </div>
                        )}
                        {analysis.mood && (
                            <div className="analysis-item">
                                <label>Mood</label>
                                <span>{analysis.mood}</span>
                            </div>
                        )}
                        {analysis.colors && (
                            <div className="analysis-item colors">
                                <label>Colores</label>
                                <div className="color-tags">
                                    {analysis.colors.map((color, i) => (
                                        <span key={i} className="color-tag">{color}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {/* Show video_prompt for first scene, next_scene_suggestion for others */}
                        {isFirstScene && analysis.video_prompt && (
                            <div className="analysis-item suggestion">
                                <label>Prompt Generado</label>
                                <p>{analysis.video_prompt}</p>
                            </div>
                        )}
                        {!isFirstScene && analysis.next_scene_suggestion && (
                            <div className="analysis-item suggestion">
                                <label>Sugerencia Siguiente Escena</label>
                                <p>{analysis.next_scene_suggestion}</p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
