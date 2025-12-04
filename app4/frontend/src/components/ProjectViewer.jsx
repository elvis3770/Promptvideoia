/**
 * Project Viewer - View completed projects with video playback
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Play, Film, Clock, Calendar } from 'lucide-react';
import { getProject, getClips, getFinalVideoUrl, getClipVideoUrl } from '../api/client';
import './ProjectViewer.css';

export default function ProjectViewer() {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [clips, setClips] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('final'); // 'final' or 'clips'

    useEffect(() => {
        loadProjectData();
    }, [projectId]);

    const loadProjectData = async () => {
        try {
            setLoading(true);
            const [projectData, clipsData] = await Promise.all([
                getProject(projectId),
                getClips(projectId)
            ]);
            setProject(projectData.project);
            setClips(clipsData.clips || []);
        } catch (error) {
            console.error('Error loading project:', error);
            alert('Error al cargar el proyecto');
        } finally {
            setLoading(false);
        }
    };

    const formatDuration = (seconds) => {
        if (!seconds) return 'N/A';
        return `${seconds.toFixed(1)}s`;
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getStatusColor = (status) => {
        const colors = {
            draft: '#6b7280',
            in_progress: '#3b82f6',
            completed: '#10b981',
            failed: '#ef4444'
        };
        return colors[status] || '#6b7280';
    };

    if (loading) {
        return <div className="viewer-loading">Cargando proyecto...</div>;
    }

    if (!project) {
        return (
            <div className="viewer-error">
                <h2>Proyecto no encontrado</h2>
                <button className="btn btn-primary" onClick={() => navigate('/')}>
                    Volver al Dashboard
                </button>
            </div>
        );
    }

    return (
        <div className="project-viewer">
            {/* Header */}
            <div className="viewer-header">
                <button className="btn-back" onClick={() => navigate('/')}>
                    <ArrowLeft size={20} />
                    Volver
                </button>
                <div className="header-info">
                    <h1>{project.name}</h1>
                    <div className="header-meta">
                        <span
                            className="status-badge"
                            style={{ backgroundColor: getStatusColor(project.status) }}
                        >
                            {project.status}
                        </span>
                        <span className="meta-item">
                            <Calendar size={16} />
                            {formatDate(project.created_at)}
                        </span>
                        <span className="meta-item">
                            <Clock size={16} />
                            {formatDuration(project.duration_target)} objetivo
                        </span>
                    </div>
                </div>
            </div>

            {/* Description */}
            {project.description && (
                <div className="project-description">
                    <p>{project.description}</p>
                </div>
            )}

            {/* Tabs */}
            <div className="viewer-tabs">
                <button
                    className={`tab ${activeTab === 'final' ? 'active' : ''}`}
                    onClick={() => setActiveTab('final')}
                >
                    <Film size={20} />
                    Video Final
                </button>
                <button
                    className={`tab ${activeTab === 'clips' ? 'active' : ''}`}
                    onClick={() => setActiveTab('clips')}
                >
                    <Play size={20} />
                    Clips Individuales ({clips.length})
                </button>
            </div>

            {/* Content */}
            <div className="viewer-content">
                {activeTab === 'final' && (
                    <div className="final-video-section">
                        {project.final_video && project.final_video.path ? (
                            <>
                                <div className="video-container">
                                    <video
                                        controls
                                        className="video-player"
                                        src={getFinalVideoUrl(projectId)}
                                    >
                                        Tu navegador no soporta el elemento de video.
                                    </video>
                                </div>
                                <div className="video-info">
                                    <div className="info-grid">
                                        <div className="info-item">
                                            <span className="label">Duración:</span>
                                            <span className="value">
                                                {formatDuration(project.final_video.metadata?.duration)}
                                            </span>
                                        </div>
                                        <div className="info-item">
                                            <span className="label">Resolución:</span>
                                            <span className="value">
                                                {project.final_video.metadata?.resolution || 'N/A'}
                                            </span>
                                        </div>
                                        <div className="info-item">
                                            <span className="label">Formato:</span>
                                            <span className="value">MP4</span>
                                        </div>
                                    </div>
                                    <a
                                        href={getFinalVideoUrl(projectId)}
                                        download={`${project.name}_final.mp4`}
                                        className="btn btn-primary"
                                    >
                                        <Download size={20} />
                                        Descargar Video Final
                                    </a>
                                </div>
                            </>
                        ) : (
                            <div className="empty-state">
                                <Film size={64} />
                                <h3>Video final no disponible</h3>
                                <p>
                                    {project.status === 'completed'
                                        ? 'El video final no se encuentra disponible.'
                                        : 'El proyecto aún no ha sido completado.'}
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'clips' && (
                    <div className="clips-section">
                        {clips.length === 0 ? (
                            <div className="empty-state">
                                <Play size={64} />
                                <h3>No hay clips disponibles</h3>
                                <p>Este proyecto aún no tiene clips generados.</p>
                            </div>
                        ) : (
                            <div className="clips-grid">
                                {clips.map((clip, index) => (
                                    <div key={clip.clip_id} className="clip-card">
                                        <div className="clip-header">
                                            <h3>
                                                Escena {clip.scene_id + 1}: {clip.scene_name}
                                            </h3>
                                            <span className="clip-duration">
                                                {formatDuration(clip.duration)}
                                            </span>
                                        </div>

                                        {clip.file && clip.file.path ? (
                                            <>
                                                <div className="clip-video-container">
                                                    <video
                                                        controls
                                                        className="clip-video"
                                                        src={getClipVideoUrl(clip.clip_id)}
                                                    >
                                                        Tu navegador no soporta el elemento de video.
                                                    </video>
                                                </div>

                                                <div className="clip-info">
                                                    {clip.prompt && (
                                                        <div className="clip-prompt">
                                                            <strong>Prompt:</strong>
                                                            <p>{clip.prompt}</p>
                                                        </div>
                                                    )}
                                                    <div className="clip-meta">
                                                        <span>Estado: {clip.status}</span>
                                                        {clip.veo_video_id && (
                                                            <span className="veo-id">
                                                                ID: {clip.veo_video_id.slice(0, 12)}...
                                                            </span>
                                                        )}
                                                    </div>
                                                    <a
                                                        href={getClipVideoUrl(clip.clip_id)}
                                                        download={`${project.name}_scene_${clip.scene_id + 1}.mp4`}
                                                        className="btn btn-secondary btn-sm"
                                                    >
                                                        <Download size={16} />
                                                        Descargar Clip
                                                    </a>
                                                </div>
                                            </>
                                        ) : (
                                            <div className="clip-unavailable">
                                                <p>Clip no disponible</p>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Project Details */}
            <div className="project-details">
                <h2>Detalles del Proyecto</h2>
                <div className="details-grid">
                    {project.subject && (
                        <div className="detail-section">
                            <h3>Sujeto</h3>
                            <p><strong>Tipo:</strong> {project.subject.type || 'N/A'}</p>
                            <p>{project.subject.description || 'Sin descripción'}</p>
                        </div>
                    )}
                    {project.product && (
                        <div className="detail-section">
                            <h3>Producto</h3>
                            <p><strong>Nombre:</strong> {project.product.name || 'N/A'}</p>
                            <p><strong>Categoría:</strong> {project.product.category || 'N/A'}</p>
                        </div>
                    )}
                    {project.brand_guidelines && (
                        <div className="detail-section">
                            <h3>Guías de Marca</h3>
                            <p><strong>Mood:</strong> {project.brand_guidelines.mood || 'N/A'}</p>
                            <p><strong>Estilo:</strong> {project.brand_guidelines.style || 'N/A'}</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
