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

    const { comparison, keywords_added, coherence_score, validation_notes, issues } = preview;

    return (
        <div className="prompt-preview">
            <div className="preview-header">
                <h3>🤖 Optimización de Prompt con IA</h3>
                <div className="coherence-badge">
                    <span className="score-label">Coherencia:</span>
                    <span className={`score-value ${getScoreClass(coherence_score)}`}>
                        {Math.round(coherence_score * 100)}%
                    </span>
                </div>
            </div>

            {/* Comparación de Acción */}
            <div className="comparison-section">
                <h4>Acción</h4>
                <div className="comparison-grid">
                    <div className="original">
                        <label>Original:</label>
                        <p className="text-content">{comparison.action.original}</p>
                    </div>
                    <div className="optimized">
                        <label>Optimizado: ✨</label>
                        <p className="text-content highlighted">{comparison.action.optimized}</p>
                        {comparison.action.improvement > 0 && (
                            <span className="improvement-badge">
                                +{comparison.action.improvement} keywords técnicas
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Comparación de Emoción */}
            <div className="comparison-section">
                <h4>Emoción</h4>
                <div className="comparison-grid">
                    <div className="original">
                        <label>Original:</label>
                        <p className="text-content">{comparison.emotion.original}</p>
                    </div>
                    <div className="optimized">
                        <label>Optimizado: ✨</label>
                        <p className="text-content highlighted">{comparison.emotion.optimized}</p>
                    </div>
                </div>
            </div>

            {/* Diálogo (si existe) */}
            {comparison.dialogue && comparison.dialogue.original && (
                <div className="comparison-section">
                    <h4>Diálogo</h4>
                    <div className="comparison-grid">
                        <div className="original">
                            <label>Original:</label>
                            <p className="text-content">"{comparison.dialogue.original}"</p>
                        </div>
                        <div className="optimized">
                            <label>Optimizado: ✨</label>
                            <p className="text-content highlighted">"{comparison.dialogue.optimized}"</p>
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
