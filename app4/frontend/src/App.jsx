/**
 * Main App Component
 */
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ProductionMonitor from './components/ProductionMonitor';
import TemplateEditor from './components/TemplateEditor';
import ProjectViewer from './components/ProjectViewer';
import About from './components/About';
import './App.css';

function App() {
    return (
        <BrowserRouter>
            <div className="app">
                <nav className="navbar">
                    <div className="nav-content">
                        <Link to="/" className="nav-brand">
                            🎬 App4 Video Generator
                        </Link>
                        <div className="nav-links">
                            <Link to="/" className="nav-link">Dashboard</Link>
                            <Link to="/about" className="nav-link">About</Link>
                        </div>
                    </div>
                </nav>

                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/new" element={<TemplateEditor />} />
                        <Route path="/project/:projectId" element={<ProjectViewer />} />
                        <Route path="/monitor/:projectId" element={<ProductionMonitor />} />
                        <Route path="/about" element={<About />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}

export default App;
