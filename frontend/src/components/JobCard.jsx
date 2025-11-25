import React from 'react';
import { Clock, CheckCircle, AlertCircle, Loader2, Download } from 'lucide-react';
import { api } from '../api/client';

const statusConfig = {
    queued: { icon: Clock, color: 'text-slate-500', bg: 'bg-slate-100' },
    processing: { icon: Loader2, color: 'text-blue-500', bg: 'bg-blue-50', animate: true },
    completed: { icon: CheckCircle, color: 'text-emerald-500', bg: 'bg-emerald-50' },
    failed: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50' },
};

const JobCard = ({ job }) => {
    const [status, setStatus] = React.useState(job.status);
    const [isPolling, setIsPolling] = React.useState(job.status === 'queued' || job.status === 'processing');

    React.useEffect(() => {
        let intervalId;

        if (isPolling) {
            intervalId = setInterval(async () => {
                try {
                    const res = await api.getJobStatus(job.id);
                    const { status: backendStatus, done } = res.data;

                    if (done || backendStatus === 'COMPLETE') {
                        setStatus('completed');
                        setIsPolling(false);
                    } else if (backendStatus === 'ERROR') {
                        setStatus('failed');
                        setIsPolling(false);
                    } else if (backendStatus === 'POLLING' || backendStatus === 'PROCESSING') {
                        setStatus('processing');
                    }
                } catch (err) {
                    console.error("Failed to poll status", err);
                }
            }, 5000); // Poll every 5 seconds
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [isPolling, job.id]);

    const config = statusConfig[status] || statusConfig.queued;
    const Icon = config.icon;

    return (
        <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-lg ${config.bg} ${config.color}`}>
                        <Icon size={16} className={config.animate ? "animate-spin" : ""} />
                    </div>
                    <span className="text-sm font-medium text-slate-700 capitalize">{status}</span>
                </div>
                <span className="text-xs text-slate-400 font-mono">{job.id.slice(0, 8)}</span>
            </div>

            <p className="text-sm text-slate-600 line-clamp-2 mb-4 h-10">
                {job.prompt || "No prompt provided"}
            </p>

            {status === 'completed' && (
                <div className="space-y-3">
                    <div className="rounded-lg overflow-hidden bg-black aspect-video">
                        <video
                            controls
                            className="w-full h-full object-contain"
                            src={api.getDownloadUrl(job.id)}
                        >
                            Your browser does not support the video tag.
                        </video>
                    </div>

                    <a
                        href={api.getDownloadUrl(job.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center gap-2 w-full py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 rounded-lg text-sm font-medium transition-colors"
                    >
                        <Download size={14} />
                        Download Video
                    </a>
                </div>
            )}
        </div>
    );
};

export default JobCard;
