import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';
import { api } from '../api/client';
import JobCard from '../components/JobCard';
import FileUploader from '../components/FileUploader';
import AdvancedSettings from '../components/AdvancedSettings';

const FirstLastFrames = () => {
    const [prompt, setPrompt] = useState('');
    const [firstFrame, setFirstFrame] = useState([]);
    const [lastFrame, setLastFrame] = useState([]);
    const [settings, setSettings] = useState({
        model: 'veo-3.1-generate-preview',
        aspect_ratio: '16:9',
        resolution: '1080p',
        duration_seconds: '8'
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [jobs, setJobs] = useState([]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (!prompt.trim() || firstFrame.length === 0 || lastFrame.length === 0) {
            setError("Please upload both first and last frames and enter a prompt");
            return;
        }

        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('prompt', prompt);
            formData.append('first_frame', firstFrame[0]);
            formData.append('last_frame', lastFrame[0]);
            formData.append('aspect_ratio', settings.aspect_ratio);
            formData.append('resolution', settings.resolution);
            formData.append('duration_seconds', settings.duration_seconds);

            const res = await api.firstLastFrames(formData);
            if (res.data.ok) {
                const newJob = {
                    id: res.data.operation_name || Date.now().toString(),
                    status: 'queued',
                    prompt: prompt,
                    type: 'first_last'
                };
                setJobs([newJob, ...jobs]);
                setPrompt('');
                setFirstFrame([]);
                setLastFrame([]);
            } else {
                setError("Backend returned an error: " + JSON.stringify(res.data));
            }
        } catch (err) {
            console.error("Failed to submit job", err);
            setError(err.response?.data?.detail || "Failed to submit job. Check backend logs.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-900">First + Last Frames</h1>
                <p className="text-slate-500">Generate smooth transitions between two images.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <FileUploader
                                    label="First Frame"
                                    files={firstFrame}
                                    onFilesChange={setFirstFrame}
                                />
                                <FileUploader
                                    label="Last Frame"
                                    files={lastFrame}
                                    onFilesChange={setLastFrame}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">Prompt</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="Describe the transition..."
                                    className="w-full h-32 p-4 rounded-xl border border-slate-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none resize-none transition-all text-slate-700 placeholder:text-slate-400"
                                />
                            </div>

                            <AdvancedSettings settings={settings} setSettings={setSettings} showModel={false} />

                            {error && (
                                <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm border border-red-100">
                                    {error}
                                </div>
                            )}

                            <div className="flex justify-end">
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="flex items-center gap-2 bg-primary hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/30"
                                >
                                    {loading ? (
                                        <span className="animate-pulse">Submitting...</span>
                                    ) : (
                                        <>
                                            <Sparkles size={18} />
                                            Generate Transition
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <div className="space-y-4">
                    <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Recent Jobs</h2>
                    {jobs.length === 0 ? (
                        <div className="text-center py-10 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                            <p className="text-slate-400 text-sm">No jobs yet</p>
                        </div>
                    ) : (
                        jobs.map(job => <JobCard key={job.id} job={job} />)
                    )}
                </div>
            </div>
        </div>
    );
};

export default FirstLastFrames;
