import axios from 'axios';

const client = axios.create({
    baseURL: '/', // Proxy handles the rest
    headers: {
        'Content-Type': 'multipart/form-data', // Default for file uploads, but axios handles it if data is FormData
    },
});

export const api = {
    textToVideo: (formData) => client.post('/text_to_video', formData),
    imageToVideo: (formData) => client.post('/image_to_video', formData),
    referenceImages: (formData) => client.post('/video_from_reference_images', formData),
    firstLastFrames: (formData) => client.post('/video_from_first_last_frames', formData),
    extendVideo: (formData) => client.post('/extend_veo_video', formData),
    getStatus: (operationName) => client.get(`/status/${operationName}`),
    getJobStatus: (operationName) => client.get(`/status/${operationName}`), // Added getJobStatus
    // Helper to construct download URL
    getDownloadUrl: (operationName) => `/download/${operationName}`,
};
