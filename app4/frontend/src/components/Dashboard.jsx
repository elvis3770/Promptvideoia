/**
 * Dashboard - Main view showing all projects
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Plus, Trash2, Download, Eye, Film } from 'lucide-react';
import { getProjects, deleteProject, startProduction, getFinalVideoUrl } from '../api/client';
import './Dashboard.css';

export default function Dashboard() {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        loadProjects();
    }, [filter]);

    const loadProjects = async () => {
        try {
            setLoading(true);
            const status = filter === 'all' ? null : filter;
            const data = await getProjects(status);
            setProjects(data.projects || []);
        } catch (error) {
            console.error('Error loading projects:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleStartProduction = async (projectId) => {
        try {
            await startProduction(projectId, true);
            alert('Production started! Check the monitor for progress.');
            navigate(`/monitor/${projectId}`);
        } catch (error) {
            alert(`Error starting production: ${error.message}`);
        }
    };

    const handleDelete = async (projectId) => {
        if (!confirm('Are you sure you want to delete this project?')) return;

        try {
            await deleteProject(projectId);
            loadProjects();
        } catch (error) {
            alert(`Error deleting project: ${error.message}`);
        }
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

    const getStatusLabel = (status) => {
        const labels = {
            draft: 'Draft',
            in_progress: 'In Progress',
            completed: 'Completed',
            failed: 'Failed'
        };
        return labels[status] || status;
    };

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <div>
                    <h1>🎬 Video Commercial Generator</h1>
                    <p>Manage your AI-powered commercial projects</p>
                </div>
                <button className="btn btn-primary" onClick={() => navigate('/new')}>
                    <Plus size={20} />
                    New Project
                </button>
            </div>

            <div className="dashboard-filters">
                <button
                    className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                    onClick={() => setFilter('all')}
                >
                    All Projects
                </button>
                <button
                    className={`filter-btn ${filter === 'draft' ? 'active' : ''}`}
                    onClick={() => setFilter('draft')}
                >
                    Drafts
                </button>
                <button
                    className={`filter-btn ${filter === 'in_progress' ? 'active' : ''}`}
                    onClick={() => setFilter('in_progress')}
                >
                    In Progress
                </button>
                <button
                    className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
                    onClick={() => setFilter('completed')}
                >
                    Completed
                </button>
            </div>

            {loading ? (
                <div className="loading">Loading projects...</div>
            ) : projects.length === 0 ? (
                <div className="empty-state">
                    <Film size={64} />
                    <h3>No projects yet</h3>
                    <p>Create your first commercial project to get started</p>
                </div>
            ) : (
                <div className="projects-grid">
                    {projects.map((project) => (
                        <div key={project.project_id} className="project-card">
                            <div className="project-header">
                                <h3>{project.name}</h3>
                                <span
                                    className="status-badge"
                                    style={{ backgroundColor: getStatusColor(project.status) }}
                                >
                                    {getStatusLabel(project.status)}
                                </span>
                            </div>

                            <div className="project-info">
                                <div className="info-item">
                                    <span className="label">Duration:</span>
                                    <span className="value">{project.duration_target}s</span>
                                </div>
                                <div className="info-item">
                                    <span className="label">Scenes:</span>
                                    <span className="value">{project.scenes?.length || 0}</span>
                                </div>
                                <div className="info-item">
                                    <span className="label">Created:</span>
                                    <span className="value">
                                        {new Date(project.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>

                            {project.description && (
                                <p className="project-description">{project.description}</p>
                            )}

                            <div className="project-actions">
                                {project.status === 'draft' && (
                                    <button
                                        className="btn btn-success btn-sm"
                                        onClick={() => handleStartProduction(project.project_id)}
                                    >
                                        <Play size={16} />
                                        Start Production
                                    </button>
                                )}

                                {project.status === 'completed' && project.final_video && (
                                    <a
                                        href={getFinalVideoUrl(project.project_id)}
                                        className="btn btn-primary btn-sm"
                                        download
                                    >
                                        <Download size={16} />
                                        Download
                                    </a>
                                )}

                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => navigate(`/project/${project.project_id}`)}
                                >
                                    <Eye size={16} />
                                    View
                                </button>

                                <button
                                    className="btn btn-danger btn-sm"
                                    onClick={() => handleDelete(project.project_id)}
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
