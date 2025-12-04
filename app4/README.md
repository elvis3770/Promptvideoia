# App4: Video Commercial Generator

Sistema automatizado de generación de videos comerciales con IA usando Google Veo 3.1.

## 🚀 Inicio Rápido

### Instalación Automática

```bash
cd app4
python setup.py
```

El script de setup instalará automáticamente:
- Dependencias de Python (backend)
- Dependencias de Node.js (frontend)
- Verificará MongoDB y FFmpeg
- Creará el archivo .env

### Configuración Manual

Si prefieres configurar manualmente:

**1. Instalar Dependencias**

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

**2. Instalar MongoDB**

- **MongoDB Local**: https://www.mongodb.com/try/download/community
- **MongoDB Atlas (Cloud)**: https://www.mongodb.com/cloud/atlas

**3. Instalar FFmpeg**

- Descargar desde: https://ffmpeg.org/download.html
- Agregar al PATH del sistema

**4. Configurar Variables de Entorno**

```bash
copy .env.example .env
```

Editar `.env`:
```env
MONGODB_URL=mongodb://localhost:27017
GOOGLE_API_KEY=tu_api_key_de_google_aqui
```

### Verificar Sistema

Antes de iniciar, verifica que todo esté configurado:

```bash
python verify_system.py
```

### Iniciar Aplicación

```bash
python start.py
```

Esto iniciará:
- **Backend** en http://localhost:8003
- **Frontend** en http://localhost:5174

Presiona `Ctrl+C` para detener ambos servicios.

## 🎨 Interfaz Web

### Dashboard
- Ver todos tus proyectos
- Filtrar por estado (Draft, In Progress, Completed)
- Crear nuevos proyectos
- Iniciar producciones
- Ver y descargar videos finales

### Editor de Templates
- Crear proyectos visualmente sin escribir JSON
- Definir información del producto y marca
- Agregar y editar escenas
- Previsualizar JSON generado
- Cargar templates desde archivos

### Monitor de Producción
- Ver progreso en tiempo real
- Estado de cada escena
- Tiempo estimado
- Notificaciones de errores

### Visor de Proyectos
- Reproducir video final
- Ver clips individuales
- Descargar videos
- Ver detalles del proyecto

## 📁 Estructura del Proyecto

```
app4/
├── backend/
│   ├── core/
│   │   ├── prompt_generator.py      # Generador de prompts
│   │   ├── continuity_engine.py     # Motor de continuidad
│   │   ├── veo_client.py            # Cliente Veo API
│   │   ├── video_assembler.py       # Ensamblador de videos
│   │   └── orchestrator.py          # Orquestador principal
│   ├── db/
│   │   ├── database.py              # Conexión MongoDB
│   │   └── repositories.py          # Repositorios CRUD
│   ├── models/
│   │   └── models.py                # Modelos Pydantic
│   └── utils/
│       └── frame_extractor.py       # Extractor de frames
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Dashboard.jsx        # Panel principal
│       │   ├── TemplateEditor.jsx   # Editor de templates
│       │   ├── ProjectViewer.jsx    # Visor de proyectos
│       │   ├── ProductionMonitor.jsx # Monitor de producción
│       │   └── About.jsx            # Información
│       └── api/
│           └── client.js            # Cliente API
├── templates/
│   ├── lve_perfume_commercial.json  # Template complejo (4 escenas)
│   ├── simple_product_showcase.json # Template simple (2 escenas)
│   └── brand_story.json             # Template medio (3 escenas)
├── api.py                           # FastAPI REST API
├── setup.py                         # Script de instalación
├── start.py                         # Script de inicio
├── verify_system.py                 # Script de verificación
├── test_production.py               # Script de prueba
└── requirements.txt
```

## 🎬 Cómo Funciona

1. **Crea un Template** - Define tu proyecto con escenas y configuración
2. **Genera Prompts** - El sistema optimiza prompts para cada escena
3. **Escena 1** - Genera primer clip (con referencias opcionales)
4. **Extrae Frame** - Obtiene último frame de Escena 1
5. **Escena 2** - Usa último frame como referencia para continuidad
6. **Repite** - Proceso continúa para todas las escenas
7. **Ensambla** - Combina clips en video final de 30s

## 🔧 Componentes Principales

### PromptGenerator
Genera prompts estructurados con niveles de refinamiento (0-3)

### ContinuityEngine
Mantiene coherencia visual frame-to-frame entre clips

### VeoClient
Cliente async para Google Veo 3.1 API

### ProductionOrchestrator
Coordina todo el proceso de producción

### VideoAssembler
Ensambla clips con FFmpeg

## 📊 Base de Datos MongoDB

### Collections

- **projects** - Proyectos con escenas y configuración
- **clips** - Clips generados con metadata
- **assets** - Imágenes de referencia y frames

## ⚙️ Configuración

### Modo Automático vs Manual

```python
result = await orchestrator.produce_commercial(
    project_template=template,
    auto_mode=True  # False para aprobación manual entre escenas
)
```

### Niveles de Refinamiento

- **0** - Prompt básico
- **1** - + Emoción
- **2** - + Especificaciones de cámara
- **3** - + Calidad cinemática

## 📝 Crear Tu Propio Template

### Opción 1: Interfaz Web (Recomendado)
1. Abre http://localhost:5174
2. Haz clic en "New Project"
3. Completa el formulario
4. Agrega escenas
5. Guarda el proyecto

### Opción 2: JSON Manual
Copia uno de los templates en `templates/` y modifica:
- `subject` - Descripción del sujeto principal
- `product` - Información del producto
- `scenes` - Define tus escenas (prompt, duración, cámara, etc.)
- `brand_guidelines` - Mood, colores, estilo

## 🎯 Guía de Uso

Ver [USAGE_GUIDE.md](USAGE_GUIDE.md) para una guía detallada paso a paso.

## ⚠️ Notas Importantes

- Cada clip tarda 2-5 minutos en generarse
- Video completo de 4 escenas: ~8-20 minutos
- Requiere FFmpeg instalado
- Modelo `veo-3.1-generate-preview` necesario para reference images
- API key de Google Veo 3.1 requerida

## 🆘 Solución de Problemas

**Error de MongoDB**: Verifica que MongoDB esté corriendo
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

**Error de API Key**: Revisa que GOOGLE_API_KEY esté configurada en .env

**Error de FFmpeg**: Instala FFmpeg y agrégalo al PATH
```bash
# Verificar instalación
ffmpeg -version
```

**Error de dependencias**: Ejecuta setup.py nuevamente
```bash
python setup.py
```

**Puerto en uso**: Cambia el puerto en api.py (línea 338) o frontend/vite.config.js

## 📚 Recursos Adicionales

- **API Docs**: http://localhost:8003/docs (cuando el backend está corriendo)
- **Google Veo 3.1**: https://ai.google.dev/gemini-api/docs/veo
- **MongoDB Docs**: https://www.mongodb.com/docs/
- **FFmpeg Docs**: https://ffmpeg.org/documentation.html

## 🤝 Contribuir

Este es un proyecto de demostración. Siéntete libre de modificarlo y adaptarlo a tus necesidades.

## 📄 Licencia

MIT License - Úsalo libremente para tus proyectos.

