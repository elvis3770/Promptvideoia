import React from 'react';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';
import './ContinuityValidator.css';

export default function ContinuityValidator({ previousElements, currentElements, onValidate }) {
    const [validation, setValidation] = React.useState(null);
    const [loading, setLoading] = React.useState(false);

    React.useEffect(() => {
        if (previousElements && currentElements) {
            validateContinuity();
        }
    }, [previousElements, currentElements]);

    const validateContinuity = async () => {
        if (!previousElements || !currentElements) return;

        setLoading(true);
        try {
            const response = await fetch('http://localhost:8003/api/continuity/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    previous_elements: previousElements,
                    current_elements: currentElements
                })
            });

            const result = await response.json();
            setValidation(result);
        } catch (error) {
            console.error('Validation error:', error);
        } finally {
            setLoading(false);
        }
    };

    if (!validation) return null;

    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'high':
                return <AlertTriangle size={16} className="severity-high" />;
            case 'medium':
                return <Info size={16} className="severity-medium" />;
            default:
                return <CheckCircle size={16} className="severity-low" />;
        }
    };

    return (
        <div className="continuity-validator">
            <div className="validator-header">
                <h4>Validación de Continuidad</h4>
                {validation.is_valid ? (
                    <span className="status-valid">
                        <CheckCircle size={16} /> Continuidad OK
                    </span>
                ) : (
                    <span className="status-invalid">
                        <AlertTriangle size={16} /> Revisar Continuidad
                    </span>
                )}
            </div>

            {validation.warnings && validation.warnings.length > 0 && (
                <div className="warnings-section">
                    <h5>⚠️ Advertencias</h5>
                    {validation.warnings.map((warning, idx) => (
                        <div key={idx} className={`warning-item severity-${warning.severity}`}>
                            {getSeverityIcon(warning.severity)}
                            <div className="warning-content">
                                <strong>{warning.element}</strong>
                                <p>{warning.message}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {validation.suggestions && validation.suggestions.length > 0 && (
                <div className="suggestions-section">
                    <h5>💡 Sugerencias</h5>
                    <ul>
                        {validation.suggestions.map((suggestion, idx) => (
                            <li key={idx}>{suggestion}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Elements comparison */}
            <div className="elements-comparison">
                <div className="comparison-column">
                    <h5>Escena Anterior</h5>
                    {previousElements.map((el, idx) => (
                        <div key={idx} className="element-card">
                            <span className="element-type">{el.type}</span>
                            <p>{el.description}</p>
                        </div>
                    ))}
                </div>
                <div className="comparison-column">
                    <h5>Escena Actual</h5>
                    {currentElements.map((el, idx) => (
                        <div key={idx} className="element-card">
                            <span className="element-type">{el.type}</span>
                            <p>{el.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
