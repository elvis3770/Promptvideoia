import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Video, Image, Layers, Film, FastForward, Activity } from 'lucide-react';
import clsx from 'clsx';

const NavItem = ({ to, icon: Icon, label }) => {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <Link
            to={to}
            className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                isActive
                    ? "bg-primary/10 text-primary font-medium"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
            )}
        >
            <Icon size={20} className={clsx(isActive ? "text-primary" : "text-slate-400 group-hover:text-slate-600")} />
            <span>{label}</span>
        </Link>
    );
};

const Layout = ({ children }) => {
    return (
        <div className="min-h-screen bg-slate-50 flex">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-slate-100 flex flex-col fixed h-full z-10">
                <div className="p-6">
                    <div className="flex items-center gap-2 text-slate-900 font-bold text-xl">
                        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white">
                            <Video size={18} />
                        </div>
                        Veo Studio
                    </div>
                    <div className="text-xs text-slate-400 mt-1 ml-10">Creator Suite</div>
                </div>

                <nav className="flex-1 px-4 space-y-1 mt-4">
                    <NavItem to="/" icon={Video} label="Text → Video" />
                    <NavItem to="/image-to-video" icon={Image} label="Image → Video" />
                    <NavItem to="/reference-images" icon={Layers} label="Reference Images" />
                    <NavItem to="/first-last" icon={Film} label="First + Last" />
                    <NavItem to="/extend" icon={FastForward} label="Extend Video" />
                </nav>

                <div className="p-4 border-t border-slate-100">
                    <div className="bg-slate-50 rounded-xl p-4">
                        <div className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
                            <Activity size={16} className="text-emerald-500" />
                            System Status
                        </div>
                        <div className="text-xs text-slate-500">Backend: Connected</div>
                        <div className="text-xs text-slate-500">Model: Veo 3.1</div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 ml-64 p-8">
                <div className="max-w-5xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default Layout;
