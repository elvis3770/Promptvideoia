# Promptvideoia 🎬✨

AI-powered commercial video generator with intelligent prompt optimization using Google Gemini and Veo 3.1.

## 🌟 Features

- 🎬 **Automated Video Generation** - Create professional commercials with Google Veo 3.1
- 🤖 **AI Prompt Optimization** - Transform simple prompts into professional descriptions with Gemini AI
- 📝 **Visual Template Editor** - Intuitive interface for creating video templates
- 🎨 **Real-time Monitoring** - Track video generation progress in real-time
- 🔄 **Scene Continuity** - Automatic visual consistency across scenes
- ✨ **Smart Enhancement** - From "woman smiles" to "elegant woman with confident smile, cinematic close-up, soft lighting..."

## 🚀 Quick Start

### Prerequisites

- Python 3.11
- Node.js 16+
- MongoDB
- Google API Key (for Veo 3.1 and Gemini)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/elvis3770/Promptvideoia.git
cd Promptvideoia
```

2. **Configure environment**
```bash
cd app4
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. **Install dependencies**
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

4. **Start the application**
```bash
# Option 1: Automatic (recommended)
py -3.11 start.py

# Option 2: Manual
# Terminal 1 - Backend
py -3.11 api.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:5174
- Backend API: http://localhost:8003
- API Docs: http://localhost:8003/docs

## 🎯 How It Works

### Traditional Flow
```
User Input → Prompt Generator → Veo 3.1 → Video
```

### With Gemini AI (NEW) ✨
```
User: "woman smiles"
   ↓
Gemini AI Optimizes
   ↓
Result: "elegant woman with confident mysterious smile, 
         cinematic close-up, soft key lighting, 
         shallow depth of field, 4K quality, professional"
   ↓
Veo 3.1 → High-Quality Video
```

## 💡 Usage Example

1. **Create a new project**
   - Click "New Project"
   - Fill in basic information (name, mood, product details)

2. **Add scenes**
   - Click "Add Scene"
   - Write a simple prompt: "woman smiles"
   - Select emotion: "confidence"

3. **Optimize with AI** ✨
   - Click "✨ Optimize with AI"
   - Review the optimized prompt
   - See keywords added and coherence score
   - Accept or reject the optimization

4. **Generate video**
   - Click "Create Project"
   - Click "Start Production"
   - Monitor progress in real-time
   - Download your professional commercial!

## 🏗️ Tech Stack

### Backend
- **Python 3.11** - Core language
- **FastAPI** - REST API framework
- **MongoDB** - Database
- **Google Gemini 2.0** - Prompt optimization
- **Google Veo 3.1** - Video generation

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client
- **Lucide React** - Icons

## 📁 Project Structure

```
app4/
├── backend/
│   ├── core/
│   │   ├── orchestrator.py          # Production coordinator
│   │   ├── prompt_engineer_agent.py # Gemini AI agent ✨
│   │   ├── prompt_validator.py      # Coherence validation ✨
│   │   ├── prompt_optimizer.py      # Keywords database ✨
│   │   ├── prompt_generator.py      # Traditional generator
│   │   ├── veo_client.py            # Veo 3.1 client
│   │   └── video_assembler.py       # Video assembly
│   ├── db/                          # Database layer
│   ├── models/                      # Data models
│   └── utils/                       # Utilities
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Dashboard.jsx
│       │   ├── TemplateEditor.jsx
│       │   ├── PromptPreview.jsx    # AI preview ✨
│       │   ├── ProductionMonitor.jsx
│       │   └── ProjectViewer.jsx
│       └── api/
│           └── client.js
└── api.py                           # Main API
```

## 🔧 Configuration

### Environment Variables

```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=video_commercial_generator

# Google APIs
GOOGLE_API_KEY=your_api_key_here

# Gemini Agent
PROMPT_OPTIMIZATION_ENABLED=true
PROMPT_OPTIMIZATION_MODEL=gemini-2.0-flash-exp
TARGET_VIDEO_MODEL=veo-3.1

# Server Ports
BACKEND_PORT=8003
FRONTEND_PORT=5174
```

## 📊 Gemini Agent Features

### Prompt Optimization
- Converts simple language to technical descriptions
- Adds cinematographic keywords
- Enhances camera specifications
- Optimizes lighting and composition

### Coherence Validation
- Detects action/emotion contradictions
- Verifies product tone compatibility
- Provides confidence score (0-100%)
- Suggests improvements

### Keywords Database
- Veo 3.1 specific keywords
- Categories: quality, lighting, camera, composition, style
- Optimized for commercial videos

## 📚 Documentation

- [Installation Guide](app4/README.md)
- [Usage Guide](app4/USAGE_GUIDE.md)
- [API Documentation](http://localhost:8003/docs)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini API for intelligent prompt optimization
- Google Veo 3.1 for high-quality video generation
- The open-source community

## 📧 Contact

- GitHub: [@elvis3770](https://github.com/elvis3770)
- Email: depositodonpedrosl@gmail.com

---

**Made with ❤️ and AI** - Transform simple ideas into professional commercial videos
