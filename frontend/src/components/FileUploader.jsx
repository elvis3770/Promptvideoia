import React, { useCallback } from 'react';
import { UploadCloud, File, X } from 'lucide-react';

const FileUploader = ({
    label = "Upload File",
    accept = "image/*",
    multiple = false,
    files = [],
    onFilesChange
}) => {

    const handleFileChange = (e) => {
        const newFiles = Array.from(e.target.files);
        if (multiple) {
            onFilesChange([...files, ...newFiles]);
        } else {
            onFilesChange(newFiles);
        }
    };

    const removeFile = (index) => {
        const newFiles = files.filter((_, i) => i !== index);
        onFilesChange(newFiles);
    };

    return (
        <div className="space-y-3">
            <label className="block text-sm font-medium text-slate-700">{label}</label>

            <div className="relative group">
                <input
                    type="file"
                    accept={accept}
                    multiple={multiple}
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 flex flex-col items-center justify-center transition-colors group-hover:border-primary/50 group-hover:bg-slate-50">
                    <div className="p-3 bg-slate-100 rounded-full mb-3 group-hover:bg-white group-hover:shadow-sm transition-all">
                        <UploadCloud size={24} className="text-slate-400 group-hover:text-primary" />
                    </div>
                    <p className="text-sm font-medium text-slate-600">
                        <span className="text-primary">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                        {accept === "image/*" ? "PNG, JPG, JPEG" : "MP4, MOV, WEBM"}
                    </p>
                </div>
            </div>

            {files.length > 0 && (
                <div className="space-y-2">
                    {files.map((file, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-white border border-slate-100 rounded-lg shadow-sm">
                            <div className="flex items-center gap-3 overflow-hidden">
                                <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                    <File size={18} className="text-slate-500" />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-sm font-medium text-slate-700 truncate">{file.name}</p>
                                    <p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                </div>
                            </div>
                            <button
                                onClick={() => removeFile(idx)}
                                className="p-1 hover:bg-slate-100 rounded-full text-slate-400 hover:text-red-500 transition-colors"
                            >
                                <X size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FileUploader;
