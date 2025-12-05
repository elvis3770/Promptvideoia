import React from 'react';
import './PromptPreview.css';

const PromptPreview = ({ preview, onAccept, onReject, loading }) => {
    if (loading) {
        return (
            <div className="prompt-preview loading">
                <div className="loading-spinner"></div>
                <p>Optimizando con Agente Gemini...</p>
            </div>
        );
    }

    if (!preview) {
        return null;
    }

    // Handle both old and new response formats
    const comparison = preview.comparison || {};
    const coherence_score = preview.coherence_score || preview.validation?.confidence_score || 0.8;
    const keywords_added = preview.keywords_added || preview.optimized?.keywords || [];
    const validation_notes = preview.validation_notes || preview.validation?.notes || '';
    const issues = preview.issues || preview.validation?.issues || [];

    // If we have direct optimized data, construct comparison from it
    const actionComparison = comparison.action || {
        original: preview.original?.action || 'N/A',
        optimized: preview.optimized?.action || 'N/A',
        improvement: 0
    };
    const emotionComparison = comparison.emotion || {
        original: preview.original?.emotion || 'N/A',
        optimized: preview.optimized?.emotion || 'N/A'
    };

    return (
        <div className="prompt-preview">
            <div className="preview-header">
                <h3>IA Optimization</h3>
                <div className="coherence-badge">
                    <span className="score-label">Coherencia:</span>
                    <span className={`score-value ${getScoreClass(coherence_score)}`}>
                        {Math.round(coherence_score * 100)}%
                    </span>
                </div>
            </div>

            {/* Comparación de Acción */}
            <div className="comparison-section">
                <h4>Accion</h4>
                <div className="comparison-grid">
                    <div className="original">
                        <label>Original:</label>
                        <p className="text-content">{actionComparison.original}</p>
                    </div>
                    <div className="optimized">
                        <label>Optimizado:</label>
                        <p className="text-content highlighted">{actionComparison.optimized}</p>
                        {actionComparison.improvement > 0 && (
                            <span className="improvement-badge">
                                +{actionComparison.improvement} keywords tecnicas
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Comparación de Emoción */}
            <div className="comparison-section">
                <h4>Emocion</h4>
                <div className="comparison-grid">
                    <div className="original">
                        <label>Original:</label>
                        <p className="text-content">{emotionComparison.original}</p>
                    </div>
                    <div className="optimized">
                        <label>Optimizado:</label>
                        <p className="text-content highlighted">{emotionComparison.optimized}</p>
                    </div>
                </div>
            </div>

            {/* Dialogo (si existe) */}
            {preview.optimized?.dialogue && preview.optimized.dialogue !== 'N/A' && (
                <div className="comparison-section">
                    <h4>Dialogo</h4>
                    <div className="comparison-grid">
                        <div className="original">
                            <label>Original:</label>
                            <p className="text-content">"{preview.original?.dialogue || 'N/A'}"</p>
                        </div>
                        <div className="optimized">
                            <label>Optimizado:</label>
                            <p className="text-content highlighted">"{preview.optimized.dialogue}"</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Keywords Agregadas */}
            {keywords_added && keywords_added.length > 0 && (
                <div className="keywords-section">
                    <h4>Keywords Técnicas Agregadas ({keywords_added.length})</h4>
                    <div className="keywords-list">
                        {keywords_added.map((keyword, index) => (
                            <span key={index} className="keyword-tag">
                                {keyword}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Notas de Validación */}
            {validation_notes && (
                <div className="validation-notes">
                    <p className="notes-icon">💡</p>
                    <p className="notes-text">{validation_notes}</p>
                </div>
            )}

            {/* Issues (si existen) */}
            {issues && issues.length > 0 && (
                <div className="issues-section">
                    <h4>⚠️ Problemas Detectados</h4>
                    <ul className="issues-list">
                        {issues.map((issue, index) => (
                            <li key={index}>{issue}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Botones de Acción */}
            <div className="preview-actions">
                <button
                    className="btn-reject"
                    onClick={onReject}
                    title="Mantener texto original"
                >
                    Usar Original
                </button>
                <button
                    className="btn-accept"
                    onClick={onAccept}
                    title="Aplicar optimización"
                >
                    ✓ Usar Optimizado
                </button>
            </div>
        </div>
    );
};

// Helper function para determinar clase de score
const getScoreClass = (score) => {
    if (score >= 0.8) return 'excellent';
    if (score >= 0.6) return 'good';
    if (score >= 0.4) return 'fair';
    return 'poor';
};

export default PromptPreview;
