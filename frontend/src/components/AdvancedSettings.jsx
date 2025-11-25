import React from 'react';
import { Settings2 } from 'lucide-react';

const AdvancedSettings = ({ settings, setSettings, showModel = false }) => {
    const handleChange = (e) => {
        const { name, value } = e.target;
        setSettings(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mb-6">
            <div className="flex items-center gap-2 mb-4 text-slate-700 font-medium">
                <Settings2 size={18} />
                <h3>Advanced Settings</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {showModel && (
                    <div className="col-span-1 md:col-span-2">
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Model
                        </label>
                        <select
                            name="model"
                            value={settings.model}
                            onChange={handleChange}
                            className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                        >
                            <option value="veo-3.1-fast-generate-preview">veo-3.1-fast-generate-preview (Faster)</option>
                            <option value="veo-3.1-generate-preview">veo-3.1-generate-preview (Higher Quality)</option>
                        </select>
                    </div>
                )}

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Aspect Ratio
                    </label>
                    <select
                        name="aspect_ratio"
                        value={settings.aspect_ratio}
                        onChange={handleChange}
                        className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    >
                        <option value="16:9">16:9 (Landscape)</option>
                        <option value="9:16">9:16 (Portrait)</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Resolution
                    </label>
                    <select
                        name="resolution"
                        value={settings.resolution}
                        onChange={handleChange}
                        className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    >
                        <option value="1080p">1080p</option>
                        <option value="720p">720p</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Duration
                    </label>
                    <select
                        name="duration_seconds"
                        value={settings.duration_seconds}
                        onChange={handleChange}
                        className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    >
                        <option value="4">4 Seconds</option>
                        <option value="6">6 Seconds</option>
                        <option value="8">8 Seconds</option>
                    </select>
                </div>
            </div>
        </div>
    );
};

export default AdvancedSettings;
