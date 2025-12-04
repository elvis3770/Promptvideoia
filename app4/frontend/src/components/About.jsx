/**
 * About - Information about App4
 */
import { Film, Zap, Layers, Video, CheckCircle, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './About.css';

export default function About() {
    const navigate = useNavigate();

    return (
        <div className="about-page">
            {/* Hero */}
            <div className="about-hero">
                <h1>🎬 App4: Video Commercial Generator</h1>
                <p className="hero-subtitle">
                    Sistema automatizado de generación de videos comerciales con IA usando Google Veo 3.1
                </p>
            </div>

            {/* Features */}
            <section className="features-section">
                <h2>Características Principales</h2>
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon">
                            <Zap size={32} />
                        </div>
                        <h3>Generación Automática</h3>
                        <p>
                            Crea videos comerciales completos automáticamente usando IA de última generación.
                            Define tus escenas y deja que Veo 3.1 genere contenido cinematográfico.
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <Layers size={32} />
                        </div>
                        <h3>Continuidad Visual</h3>
                        <p>
                            Motor de continuidad que mantiene coherencia entre escenas usando el último
                            frame de cada clip como referencia para el siguiente.
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <Film size={32} />
                        </div>
                        <h3>Templates Personalizables</h3>
                        <p>
                            Crea y edita templates con múltiples escenas. Define prompts, emociones,
                            movimientos de cámara, iluminación y más.
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <Video size={32} />
                        </div>
                        <h3>Ensamblado Profesional</h3>
                        <p>
                            Combina clips individuales en un video final cohesivo usando FFmpeg con
                            transiciones suaves y calidad profesional.
                        </p>
                    </div>
                </div>
            </section>

            {/* How it Works */}
            <section className="workflow-section">
                <h2>Cómo Funciona</h2>
                <div className="workflow-steps">
                    <div className="workflow-step">
                        <div className="step-number">1</div>
                        <div className="step-content">
                            <h3>Crea un Template</h3>
                            <p>
                                Define tu proyecto con información del producto, sujeto principal,
                                guías de marca y escenas individuales.
                            </p>
                        </div>
                    </div>
                    <ArrowRight className="step-arrow" size={24} />
                    <div className="workflow-step">
                        <div className="step-number">2</div>
                        <div className="step-content">
                            <h3>Inicia la Producción</h3>
                            <p>
                                El orquestador genera prompts optimizados y coordina la generación
                                de cada escena con Google Veo 3.1.
                            </p>
                        </div>
                    </div>
                    <ArrowRight className="step-arrow" size={24} />
                    <div className="workflow-step">
                        <div className="step-number">3</div>
                        <div className="step-content">
                            <h3>Monitorea el Progreso</h3>
                            <p>
                                Observa en tiempo real cómo se genera cada escena. El sistema
                                mantiene continuidad visual entre clips.
                            </p>
                        </div>
                    </div>
                    <ArrowRight className="step-arrow" size={24} />
                    <div className="workflow-step">
                        <div className="step-number">4</div>
                        <div className="step-content">
                            <h3>Descarga el Resultado</h3>
                            <p>
                                Obtén tu video comercial completo listo para usar, junto con
                                los clips individuales de cada escena.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Tech Stack */}
            <section className="tech-section">
                <h2>Tecnologías Utilizadas</h2>
                <div className="tech-grid">
                    <div className="tech-item">
                        <h4>Backend</h4>
                        <ul>
                            <li>Python 3.8+</li>
                            <li>FastAPI</li>
                            <li>Google Veo 3.1 API</li>
                            <li>MongoDB</li>
                            <li>FFmpeg</li>
                        </ul>
                    </div>
                    <div className="tech-item">
                        <h4>Frontend</h4>
                        <ul>
                            <li>React 18</li>
                            <li>Vite</li>
                            <li>React Router</li>
                            <li>Axios</li>
                            <li>Lucide Icons</li>
                        </ul>
                    </div>
                    <div className="tech-item">
                        <h4>Componentes Core</h4>
                        <ul>
                            <li>PromptGenerator</li>
                            <li>ContinuityEngine</li>
                            <li>VeoClient</li>
                            <li>ProductionOrchestrator</li>
                            <li>VideoAssembler</li>
                        </ul>
                    </div>
                </div>
            </section>

            {/* Quick Start */}
            <section className="quickstart-section">
                <h2>Inicio Rápido</h2>
                <div className="quickstart-content">
                    <div className="quickstart-steps">
                        <div className="quickstart-item">
                            <CheckCircle size={20} />
                            <span>Instala MongoDB y configura tu API key de Google</span>
                        </div>
                        <div className="quickstart-item">
                            <CheckCircle size={20} />
                            <span>Ejecuta el script de configuración: <code>python setup.py</code></span>
                        </div>
                        <div className="quickstart-item">
                            <CheckCircle size={20} />
                            <span>Inicia el sistema: <code>python start.py</code></span>
                        </div>
                        <div className="quickstart-item">
                            <CheckCircle size={20} />
                            <span>Abre tu navegador en <code>http://localhost:5174</code></span>
                        </div>
                    </div>
                    <button
                        className="btn btn-primary btn-large"
                        onClick={() => navigate('/new')}
                    >
                        <Film size={24} />
                        Crear Tu Primer Proyecto
                    </button>
                </div>
            </section>

            {/* Notes */}
            <section className="notes-section">
                <h2>Notas Importantes</h2>
                <div className="notes-grid">
                    <div className="note-card note-info">
                        <h4>⏱️ Tiempo de Generación</h4>
                        <p>
                            Cada clip tarda aproximadamente 2-5 minutos en generarse.
                            Un video completo de 4 escenas puede tomar entre 8-20 minutos.
                        </p>
                    </div>
                    <div className="note-card note-warning">
                        <h4>🔑 API Key Requerida</h4>
                        <p>
                            Necesitas una API key válida de Google Cloud con acceso a Veo 3.1.
                            Configúrala en el archivo <code>.env</code>.
                        </p>
                    </div>
                    <div className="note-card note-tip">
                        <h4>🎨 Mejores Prácticas</h4>
                        <p>
                            Para mejores resultados, usa prompts detallados y específicos.
                            Define claramente la emoción, iluminación y movimiento de cámara.
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}
