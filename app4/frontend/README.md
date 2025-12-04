# App4 Frontend - Video Commercial Generator

Interfaz web moderna para gestionar proyectos de generación de videos comerciales con IA.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en `frontend/`:

```env
VITE_API_URL=http://localhost:8003
```

### 3. Ejecutar Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: http://localhost:5174

## 📁 Estructura

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # Cliente API con Axios
│   ├── components/
│   │   ├── Dashboard.jsx      # Dashboard principal
│   │   ├── Dashboard.css
│   │   ├── ProductionMonitor.jsx  # Monitor en tiempo real
│   │   └── ProductionMonitor.css
│   ├── App.jsx                # Componente principal
│   ├── App.css
│   ├── main.jsx               # Punto de entrada
│   └── index.css
├── index.html
├── package.json
└── vite.config.js
```

## 🎨 Componentes

### Dashboard
- Lista de todos los proyectos
- Filtros por estado (Draft, In Progress, Completed)
- Acciones: Start Production, Download, View, Delete
- Grid responsive

### Production Monitor
- Monitoreo en tiempo real (polling cada 5s)
- Progreso por escena
- Indicadores de estado visual
- Mensajes de error/éxito

## 🔌 API Integration

El frontend se comunica con el backend FastAPI en puerto 8003:

- `GET /api/projects` - Lista de proyectos
- `POST /api/projects` - Crear proyecto
- `POST /api/production/start` - Iniciar producción
- `GET /api/production/status/{id}` - Estado de producción
- `GET /api/video/{id}/final` - Descargar video final

## 🎯 Características

✅ Dashboard moderno con grid responsive
✅ Filtros de proyectos por estado
✅ Monitor de producción en tiempo real
✅ Indicadores visuales de progreso
✅ Descarga de videos finales
✅ Navegación con React Router
✅ Diseño limpio y profesional

## 📦 Dependencias

- **React 18** - UI library
- **React Router** - Navegación
- **Axios** - HTTP client
- **Lucide React** - Iconos
- **Framer Motion** - Animaciones (opcional)
- **Vite** - Build tool

## 🚀 Producción

```bash
npm run build
npm run preview
```

Los archivos de producción estarán en `dist/`.
