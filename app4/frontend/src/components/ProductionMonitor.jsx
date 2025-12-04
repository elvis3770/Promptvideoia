/**
 * Production Monitor - Real-time production status
 */
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Film, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
import { getProductionStatus, getProject } from '../api/client';
import './ProductionMonitor.css';

export default function ProductionMonitor() {
    const { projectId } = useParams();
    const [project, setProject] = useState(null);
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadProject();
        const interval = setInterval(checkStatus, 5000); // Poll every 5 seconds
        return () => clearInterval(interval);
    }, [projectId]);

    const loadProject = async () => {
        try {
            const data = await getProject(projectId);
            setProject(data.project);
        } catch (error) {
            console.error('Error loading project:', error);
        }
    };

    const checkStatus = async () => {
        try {
            const data = await getProductionStatus(projectId);
            setStatus(data);
            setLoading(false);

            // Reload project if completed
            if (data.status === 'completed') {
                loadProject();
            }
        } catch (error) {
            console.error('Error checking status:', error);
            setLoading(false);
        }
    };

    const getSceneStatus = (sceneId) => {
        if (!project) return 'pending';
        const scene = project.scenes?.find(s => s.scene_id === sceneId);
        return scene?.status || 'pending';
    };

    const getStatusIcon = (sceneStatus) => {
        switch (sceneStatus) {
            case 'completed':
                return <CheckCircle className="icon-success" size={20} />;
            case 'generating':
                return <Loader className="icon-loading spin" size={20} />;
            case 'failed':
                return <XCircle className="icon-error" size={20} />;
            default:
                return <Clock className="icon-pending" size={20} />;
        }
    };

    if (loading) {
        return <div className="monitor-loading">Loading production status...</div>;
    }

    return (
        <div className="production-monitor">
            <div className="monitor-header">
                <Film size={32} />
                <div>
                    <h1>{project?.name || 'Production Monitor'}</h1>
                    <p>Real-time production status</p>
                </div>
            </div>

            <div className="monitor-status">
                <div className="status-card">
                    <h3>Overall Status</h3>
                    <div className={`status-indicator status-${status?.status || 'unknown'}`}>
                        {status?.status?.toUpperCase() || 'UNKNOWN'}
                    </div>
                </div>

                {status?.started_at && (
                    <div className="status-card">
                        <h3>Started</h3>
                        <p>{new Date(status.started_at).toLocaleString()}</p>
                    </div>
                )}

                {status?.current_scene !== undefined && (
                    <div className="status-card">
                        <h3>Progress</h3>
                        <p>
                            Scene {status.current_scene} of {status.total_scenes}
                        </p>
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{
                                    width: `${(status.current_scene / status.total_scenes) * 100}%`
                                }}
                            />
                        </div>
                    </div>
                )}
            </div>

            {project?.scenes && (
                <div className="scenes-list">
                    <h2>Scenes</h2>
                    {project.scenes.map((scene, idx) => {
                        const sceneStatus = getSceneStatus(scene.scene_id);
                        return (
                            <div key={scene.scene_id} className={`scene-item scene-${sceneStatus}`}>
                                <div className="scene-number">{idx + 1}</div>
                                <div className="scene-info">
                                    <h4>{scene.name}</h4>
                                    <p>{scene.duration}s • {scene.emotion}</p>
                                </div>
                                <div className="scene-status">
                                    {getStatusIcon(sceneStatus)}
                                    <span>{sceneStatus}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {status?.error && (
                <div className="error-message">
                    <XCircle size={20} />
                    <div>
                        <h4>Production Failed</h4>
                        <p>{status.error}</p>
                    </div>
                </div>
            )}

            {status?.status === 'completed' && status?.result && (
                <div className="success-message">
                    <CheckCircle size={20} />
                    <div>
                        <h4>Production Completed!</h4>
                        <p>Final video: {status.result.final_video}</p>
                        <p>Duration: {status.result.metadata?.duration?.toFixed(1)}s</p>
                    </div>
                </div>
            )}
        </div>
    );
}
