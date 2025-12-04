/**
 * API Client for App4 Backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8003';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Projects
export const getProjects = async (status = null, limit = 50) => {
    const params = {};
    if (status) params.status = status;
    if (limit) params.limit = limit;

    const response = await api.get('/api/projects', { params });
    return response.data;
};

export const getProject = async (projectId) => {
    const response = await api.get(`/api/projects/${projectId}`);
    return response.data;
};

export const createProject = async (template, autoMode = true) => {
    const response = await api.post('/api/projects', {
        template,
        auto_mode: autoMode,
    });
    return response.data;
};

export const deleteProject = async (projectId) => {
    const response = await api.delete(`/api/projects/${projectId}`);
    return response.data;
};

// Production
export const startProduction = async (projectId, autoMode = true) => {
    const response = await api.post('/api/production/start', {
        project_id: projectId,
        auto_mode: autoMode,
    });
    return response.data;
};

export const getProductionStatus = async (projectId) => {
    const response = await api.get(`/api/production/status/${projectId}`);
    return response.data;
};

// Clips
export const getClips = async (projectId) => {
    const response = await api.get(`/api/clips/${projectId}`);
    return response.data;
};

export const getClipByScene = async (projectId, sceneId) => {
    const response = await api.get(`/api/clips/${projectId}/${sceneId}`);
    return response.data;
};

// Videos
export const getFinalVideoUrl = (projectId) => {
    return `${API_BASE_URL}/api/video/${projectId}/final`;
};

export const getClipVideoUrl = (clipId) => {
    return `${API_BASE_URL}/api/video/clip/${clipId}`;
};

// Prompt Optimization
export const optimizePrompt = async (data) => {
    const response = await api.post('/api/prompts/optimize', data);
    return response.data;
};

export const validatePrompt = async (data) => {
    const response = await api.post('/api/prompts/validate', data);
    return response.data;
};

export const getKeywords = async (model = 'veo-3.1') => {
    const response = await api.get(`/api/prompts/keywords/${model}`);
    return response.data;
};

export default api;
