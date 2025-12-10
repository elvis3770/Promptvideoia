# Prompt Comercial - AI Video Prompt Optimizer

Herramienta de optimización de prompts para generación de videos comerciales con IA, usando Gemini para mejorar descripciones y mantener continuidad visual entre escenas.

## 🎯 Características

- ✅ **Optimización de prompts con IA** - Mejora automática de descripciones usando Gemini (gratis vía WebAI)
- ✅ **Análisis de imágenes con contexto** - Gemini analiza tu imagen del producto y combina esa información visual con tu acción deseada
- ✅ **Optimización consciente de imagen** - Para la primera escena, el sistema recuerda lo que vio en la imagen al optimizar tu prompt
- ✅ **Continuidad visual automática** - Analiza el último frame de escenas anteriores para mantener coherencia
- ✅ **Interfaz drag-and-drop** - Sube imágenes fácilmente
- ✅ **Preview de optimizaciones** - Revisa cambios antes de aplicar
- ✅ **Modo dual** - WebAI (gratis) para texto + API oficial (visión) para imágenes

## 🏗️ Arquitectura

```
Frontend (React + Vite)  →  Backend (FastAPI)  →  Gemini AI
    localhost:5174            localhost:8003         
                                    ↓
                        ┌───────────┴───────────┐
                        ↓                       ↓
                  WebAI-to-API            Google Gemini API
                  (Texto - Gratis)        (Imágenes - Paga)
```

## 📋 Requisitos

- Python 3.10+
- Node.js 18+
- MongoDB (opcional, para persistencia)
- WebAI-to-API server (para modo gratis)
- Google Gemini API key (para análisis de imágenes)

## 🚀 Instalación

### 1. Clonar repositorio

```bash
git clone https://github.com/elvis3770/prompt-comercial.git
cd prompt-comercial
```

### 2. Backend

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Frontend

```bash
cd frontend
npm install
```

### 4. WebAI-to-API (opcional, para modo gratis)

Sigue las instrucciones en: https://github.com/Zai-Kun/WebAI-to-API

## ⚙️ Configuración

### Archivo `.env`

```env
# Gemini API Key - Para análisis de imágenes
GEMINI_API_KEY=tu_api_key_aqui

# WebAI-to-API - Para optimización de texto (gratis)
USE_LOCAL_GEMINI=true
WEBAI_API_BASE_URL=http://localhost:6969/v1

# MongoDB (opcional)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=prompt_comercial

# Puertos
BACKEND_PORT=8003
FRONTEND_PORT=5174
```

## 🎮 Uso

### Iniciar servidores

```bash
# Terminal 1: WebAI-to-API (si usas modo gratis)
cd path/to/WebAI-to-API/src
python run.py

# Terminal 2: Backend + Frontend
cd prompt-comercial
python start.py
```

Abre http://localhost:5174 en tu navegador.

### Flujo de trabajo

1. **Crear escena** - Escribe un prompt básico
2. **Optimizar** - Click en "Optimizar con IA" (usa WebAI gratis)
3. **Subir frame** - Arrastra el último frame de la escena anterior
4. **Analizar** - Gemini analiza la imagen y sugiere cómo empezar la siguiente escena
5. **Aplicar** - La sugerencia se agrega automáticamente al prompt
6. **Optimizar nuevamente** - Refina el prompt completo con continuidad

## 💰 Costos

| Operación | Método | Costo |
|-----------|--------|-------|
| Optimizar texto | WebAI-to-API | **Gratis** (cookies) |
| Analizar imagen | API Oficial | **~$0.002/imagen** |

## 📁 Estructura del Proyecto

```
prompt-comercial/
├── backend/
│   ├── core/
│   │   ├── prompt_engineer_agent.py  # Lógica de optimización
│   │   ├── webai_client.py           # Cliente WebAI
│   │   └── prompt_orchestrator.py    # Orquestador
│   └── utils/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── TemplateEditor.jsx    # Editor de escenas
│       │   ├── FrameUploader.jsx     # Upload de imágenes
│       │   └── PromptPreview.jsx     # Preview de optimizaciones
│       └── api/
│           └── client.js             # Cliente API
├── api.py                            # FastAPI endpoints
├── start.py                          # Launcher
└── requirements.txt
```

## 🔧 Endpoints API

### POST `/api/prompts/optimize`
Optimiza un prompt de texto usando Gemini (vía WebAI).

**Request:**
```json
{
  "action": "mujer sosteniendo perfume",
  "emotion": "elegante",
  "product_tone": "luxury"
}
```

**Response:**
```json
{
  "ok": true,
  "optimized": {
    "action": "Elegant woman gracefully holding luxury perfume...",
    "emotion": "sophisticated"
  }
}
```

### POST `/api/prompts/analyze-frame`
Analiza una imagen para extraer información de continuidad.

**Request:**
```json
{
  "image_data": "base64_encoded_image",
  "mime_type": "image/jpeg"
}
```

**Response:**
```json
{
  "ok": true,
  "analysis": {
    "subject_position": "center",
    "camera_angle": "medium shot",
    "lighting": "soft studio",
    "colors": ["purple", "red"],
    "mood": "elegant",
    "next_scene_suggestion": "Start with close-up of hand..."
  }
}
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

MIT License - ver archivo LICENSE para más detalles.

## 🙏 Agradecimientos

- [WebAI-to-API](https://github.com/Zai-Kun/WebAI-to-API) - Acceso gratis a Gemini
- [Google Gemini](https://ai.google.dev/) - Modelo de IA
- FastAPI, React, Vite - Frameworks utilizados

## 📧 Contacto

Elvis - [@elvis3770](https://github.com/elvis3770)

Project Link: https://github.com/elvis3770/prompt-comercial
