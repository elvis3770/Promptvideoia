/**
 * Template Editor - Create and edit project templates
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Trash2, Save, Upload, Eye, Sparkles } from 'lucide-react';
import { createProject, optimizePrompt } from '../api/client';
import PromptPreview from './PromptPreview';
import FrameUploader from './FrameUploader';
import ContinuityValidator from './ContinuityValidator';
import './TemplateEditor.css';

export default function TemplateEditor() {
    const navigate = useNavigate();
    const [showPreview, setShowPreview] = useState(false);
    const [optimizationPreview, setOptimizationPreview] = useState(null);
    const [optimizingScene, setOptimizingScene] = useState(null);
    const [loading, setLoading] = useState(false);
    const [imageAnalysis, setImageAnalysis] = useState({});  // Store image analysis per scene
    const [template, setTemplate] = useState({
        name: '',
        description: '',
        duration_target: 30,
        subject: {
            type: '',
            description: ''
        },
        product: {
            name: '',
            category: '',
            key_features: []
        },
        brand_guidelines: {
            mood: '',
            color_palette: [],
            style: ''
        },
        scenes: []
    });

    const addScene = () => {
        const newScene = {
            scene_id: template.scenes.length,
            name: `Scene ${template.scenes.length + 1}`,
            duration: 7.5,
            prompt: '',
            emotion: 'neutral',
            camera_movement: 'static',
            lighting: 'natural',
            reference_images: []
        };
        setTemplate({
            ...template,
            scenes: [...template.scenes, newScene]
        });
    };

    const removeScene = (index) => {
        const newScenes = template.scenes.filter((_, i) => i !== index);
        // Renumber scene_ids
        newScenes.forEach((scene, i) => {
            scene.scene_id = i;
            scene.name = `Scene ${i + 1}`;
        });
        setTemplate({
            ...template,
            scenes: newScenes
        });
    };

    const updateScene = (index, field, value) => {
        const newScenes = [...template.scenes];
        newScenes[index] = {
            ...newScenes[index],
            [field]: value
        };
        setTemplate({
            ...template,
            scenes: newScenes
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate
        if (!template.name || template.scenes.length === 0) {
            alert('Por favor completa el nombre y agrega al menos una escena');
            return;
        }

        try {
            const result = await createProject(template, true);
            alert('¡Proyecto creado exitosamente!');
            navigate('/');
        } catch (error) {
            alert(`Error al crear proyecto: ${error.message}`);
        }
    };

    const loadFromFile = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                setTemplate(data);
            } catch (error) {
                alert('Error al cargar archivo: formato JSON inválido');
            }
        };
        reader.readAsText(file);
    };

    const downloadTemplate = () => {
        const dataStr = JSON.stringify(template, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        const exportFileDefaultName = `${template.name || 'template'}.json`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    };

    const handleOptimize = async (sceneIndex) => {
        const scene = template.scenes[sceneIndex];

        setOptimizingScene(sceneIndex);
        setLoading(true);

        try {
            // Prepare optimization request
            const optimizationRequest = {
                action: scene.prompt || '',
                emotion: scene.emotion || 'neutral',
                dialogue: scene.dialogue || '',
                voice_gender: scene.voice_gender || 'female',
                product_tone: template.brand_guidelines.mood || 'professional',
                scene_type: 'general'
            };

            // Add image context if this is first scene and we have analysis
            if (sceneIndex === 0 && imageAnalysis[0]) {
                optimizationRequest.image_context = imageAnalysis[0];
            }

            const result = await optimizePrompt(optimizationRequest);

            if (result.ok) {
                // Format preview with original and optimized data
                setOptimizationPreview({
                    sceneIndex,
                    original: {
                        action: scene.prompt || 'Sin prompt',
                        emotion: scene.emotion || 'neutral'
                    },
                    optimized: result.optimized,
                    validation: result.validation,
                    optimizedData: result.optimized
                });
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            alert(`Error al optimizar: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const applyOptimization = () => {
        if (!optimizationPreview) return;

        const { sceneIndex, optimizedData } = optimizationPreview;
        const newScenes = [...template.scenes];

        // Aplicar prompt optimizado - use 'action' instead of 'optimized_action'
        newScenes[sceneIndex] = {
            ...newScenes[sceneIndex],
            prompt: optimizedData.action || optimizedData.optimized_action || newScenes[sceneIndex].prompt,
            emotion: optimizedData.emotion || optimizedData.optimized_emotion || newScenes[sceneIndex].emotion
        };

        setTemplate({
            ...template,
            scenes: newScenes
        });

        setOptimizationPreview(null);
        setOptimizingScene(null);
    };

    const rejectOptimization = () => {
        setOptimizationPreview(null);
        setOptimizingScene(null);
    };

    return (
        <div className="template-editor">
            <div className="editor-header">
                <h1>📝 Editor de Templates</h1>
                <div className="header-actions">
                    <label className="btn btn-secondary">
                        <Upload size={20} />
                        Cargar JSON
                        <input
                            type="file"
                            accept=".json"
                            onChange={loadFromFile}
                            style={{ display: 'none' }}
                        />
                    </label>
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => setShowPreview(!showPreview)}
                    >
                        <Eye size={20} />
                        {showPreview ? 'Ocultar' : 'Ver'} JSON
                    </button>
                </div>
            </div>

            {showPreview && (
                <div className="json-preview">
                    <pre>{JSON.stringify(template, null, 2)}</pre>
                </div>
            )}

            <form onSubmit={handleSubmit} className="editor-form">
                {/* Basic Info */}
                <section className="form-section">
                    <h2>Información Básica</h2>
                    <div className="form-grid">
                        <div className="form-group">
                            <label>Nombre del Proyecto *</label>
                            <input
                                type="text"
                                value={template.name}
                                onChange={(e) => setTemplate({ ...template, name: e.target.value })}
                                placeholder="Mi Comercial Increíble"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Duración Total (segundos)</label>
                            <input
                                type="number"
                                value={template.duration_target}
                                onChange={(e) => setTemplate({ ...template, duration_target: Number(e.target.value) })}
                                min="10"
                                max="60"
                            />
                        </div>
                        <div className="form-group full-width">
                            <label>Descripción</label>
                            <textarea
                                value={template.description}
                                onChange={(e) => setTemplate({ ...template, description: e.target.value })}
                                placeholder="Descripción breve del proyecto..."
                                rows="2"
                            />
                        </div>
                    </div>
                </section>

                {/* Subject */}
                <section className="form-section">
                    <h2>Sujeto Principal</h2>
                    <div className="form-grid">
                        <div className="form-group">
                            <label>Tipo</label>
                            <input
                                type="text"
                                value={template.subject.type}
                                onChange={(e) => setTemplate({
                                    ...template,
                                    subject: { ...template.subject, type: e.target.value }
                                })}
                                placeholder="persona, producto, animal..."
                            />
                        </div>
                        <div className="form-group full-width">
                            <label>Descripción</label>
                            <textarea
                                value={template.subject.description}
                                onChange={(e) => setTemplate({
                                    ...template,
                                    subject: { ...template.subject, description: e.target.value }
                                })}
                                placeholder="Descripción detallada del sujeto..."
                                rows="2"
                            />
                        </div>
                    </div>
                </section>

                {/* Product */}
                <section className="form-section">
                    <h2>Producto</h2>
                    <div className="form-grid">
                        <div className="form-group">
                            <label>Nombre del Producto</label>
                            <input
                                type="text"
                                value={template.product.name}
                                onChange={(e) => setTemplate({
                                    ...template,
                                    product: { ...template.product, name: e.target.value }
                                })}
                                placeholder="Nombre del producto"
                            />
                        </div>
                        <div className="form-group">
                            <label>Categoría</label>
                            <input
                                type="text"
                                value={template.product.category}
                                onChange={(e) => setTemplate({
                                    ...template,
                                    product: { ...template.product, category: e.target.value }
                                })}
                                placeholder="perfume, tecnología, alimentos..."
                            />
                        </div>
                    </div>
                </section>

                {/* Brand Guidelines */}
                <section className="form-section">
                    <h2>Guías de Marca</h2>
                    <div className="form-grid">
                        <div className="form-group">
                            <label>Mood/Ambiente</label>
                            <input
                                type="text"
                                value={template.brand_guidelines.mood}
                                onChange={(e) => setTemplate({
                                    ...template,
                                    brand_guidelines: { ...template.brand_guidelines, mood: e.target.value }
                                })}
                                placeholder="elegante, moderno, juvenil..."
                            />
                        </div>
                        <div className="form-group">
                            <label>Estilo</label>
                            <input
                                type="text"
                                value={template.brand_guidelines.style}
                                onChange={(e) => setTemplate({
                                    ...template,
                                    brand_guidelines: { ...template.brand_guidelines, style: e.target.value }
                                })}
                                placeholder="minimalista, cinematográfico..."
                            />
                        </div>
                    </div>
                </section>

                {/* Scenes */}
                <section className="form-section">
                    <div className="section-header">
                        <h2>Escenas ({template.scenes.length})</h2>
                        <button type="button" className="btn btn-primary" onClick={addScene}>
                            <Plus size={20} />
                            Agregar Escena
                        </button>
                    </div>

                    {template.scenes.length === 0 ? (
                        <div className="empty-state">
                            <p>No hay escenas. Agrega al menos una escena para continuar.</p>
                        </div>
                    ) : (
                        <div className="scenes-list">
                            {template.scenes.map((scene, index) => (
                                <div key={index} className="scene-card">
                                    <div className="scene-header">
                                        <h3>Escena {index + 1}</h3>
                                        <button
                                            type="button"
                                            className="btn-icon btn-danger"
                                            onClick={() => removeScene(index)}
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                    <div className="form-grid">
                                        <div className="form-group">
                                            <label>Nombre</label>
                                            <input
                                                type="text"
                                                value={scene.name}
                                                onChange={(e) => updateScene(index, 'name', e.target.value)}
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Duración (s)</label>
                                            <input
                                                type="number"
                                                value={scene.duration}
                                                onChange={(e) => updateScene(index, 'duration', Number(e.target.value))}
                                                min="5"
                                                max="15"
                                                step="0.5"
                                            />
                                        </div>
                                        <div className="form-group full-width">
                                            <label>Prompt</label>
                                            <textarea
                                                value={scene.prompt}
                                                onChange={(e) => updateScene(index, 'prompt', e.target.value)}
                                                placeholder="Descripción de lo que sucede en esta escena..."
                                                rows="3"
                                            />
                                        </div>
                                        <div className="form-group full-width">
                                            <label>Diálogo (Español Argentino)</label>
                                            <textarea
                                                value={scene.dialogue || ''}
                                                onChange={(e) => updateScene(index, 'dialogue', e.target.value)}
                                                placeholder="Ej: 'Este es el aroma de la elegancia, che'"
                                                rows="2"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Voz</label>
                                            <select
                                                value={scene.voice_gender || 'female'}
                                                onChange={(e) => updateScene(index, 'voice_gender', e.target.value)}
                                            >
                                                <option value="female">Mujer</option>
                                                <option value="male">Hombre</option>
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label>Emoción</label>
                                            <select
                                                value={scene.emotion}
                                                onChange={(e) => updateScene(index, 'emotion', e.target.value)}
                                            >
                                                <option value="neutral">Neutral</option>
                                                <option value="joy">Alegría</option>
                                                <option value="excitement">Emoción</option>
                                                <option value="calm">Calma</option>
                                                <option value="mystery">Misterio</option>
                                                <option value="luxury">Lujo</option>
                                            </select>
                                        </div>
                                        <div className="form-group full-width">
                                            <label>Prompt Negativo (qué NO quieres)</label>
                                            <textarea
                                                value={scene.negative_prompt || ''}
                                                onChange={(e) => updateScene(index, 'negative_prompt', e.target.value)}
                                                placeholder="Ej: no text, no blurry, no distortions, no watermark"
                                                rows="2"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label>Movimiento de Cámara</label>
                                            <select
                                                value={scene.camera_movement}
                                                onChange={(e) => updateScene(index, 'camera_movement', e.target.value)}
                                            >
                                                <option value="static">Estática</option>
                                                <option value="slow_pan">Pan Lento</option>
                                                <option value="dolly_in">Dolly In</option>
                                                <option value="dolly_out">Dolly Out</option>
                                                <option value="tracking">Tracking</option>
                                                <option value="crane">Crane</option>
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label>Iluminación</label>
                                            <select
                                                value={scene.lighting}
                                                onChange={(e) => updateScene(index, 'lighting', e.target.value)}
                                            >
                                                <option value="natural">Natural</option>
                                                <option value="soft">Suave</option>
                                                <option value="dramatic">Dramática</option>
                                                <option value="golden_hour">Golden Hour</option>
                                                <option value="studio">Estudio</option>
                                            </select>
                                        </div>
                                    </div>

                                    {/* Botón de Optimización con IA */}
                                    <div className="optimization-section">
                                        <button
                                            type="button"
                                            className="btn btn-ai"
                                            onClick={() => handleOptimize(index)}
                                            disabled={loading && optimizingScene === index}
                                        >
                                            <Sparkles size={18} />
                                            {loading && optimizingScene === index
                                                ? 'Optimizando...'
                                                : 'Optimizar con IA'}
                                        </button>
                                    </div>

                                    {/* Preview de Optimización */}
                                    {optimizationPreview && optimizationPreview.sceneIndex === index && (
                                        <PromptPreview
                                            preview={optimizationPreview}
                                            onAccept={applyOptimization}
                                            onReject={rejectOptimization}
                                            loading={false}
                                        />
                                    )}

                                    {/* Frame Uploader para referencia visual */}
                                    <FrameUploader
                                        isFirstScene={index === 0}
                                        onAnalysisComplete={(analysis) => {
                                            // Save analysis for optimization
                                            setImageAnalysis(prev => ({
                                                ...prev,
                                                [index]: analysis
                                            }));

                                            if (index === 0) {
                                                // First scene: DON'T replace prompt field
                                                // Keep it empty so user can write their action
                                                // The video_prompt is saved in imageAnalysis and will be used during optimization
                                                console.log('[First Scene] video_prompt saved in imageAnalysis, Prompt field kept empty for user action');
                                            } else {
                                                // Subsequent scenes: Add continuity suggestion
                                                const continuityContext = analysis.next_scene_suggestion || '';
                                                const currentPrompt = scene.prompt || '';
                                                if (continuityContext && !currentPrompt.includes('[CONTINUITY]')) {
                                                    updateScene(index, 'prompt',
                                                        `[CONTINUITY: ${continuityContext}] ${currentPrompt}`
                                                    );
                                                }
                                            }
                                        }}
                                    />

                                    {/* Continuity Validator for scenes 2+ */}
                                    {index > 0 && imageAnalysis[index - 1] && imageAnalysis[index] && (
                                        <ContinuityValidator
                                            previousElements={imageAnalysis[index - 1].tracked_elements || []}
                                            currentElements={imageAnalysis[index].tracked_elements || []}
                                        />
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </section>

                {/* Actions */}
                <div className="form-actions">
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => navigate('/')}
                    >
                        Cancelar
                    </button>
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={downloadTemplate}
                    >
                        <Save size={20} />
                        Descargar JSON
                    </button>
                    <button type="submit" className="btn btn-success">
                        <Plus size={20} />
                        Crear Proyecto
                    </button>
                </div>
            </form>
        </div>
    );
}
