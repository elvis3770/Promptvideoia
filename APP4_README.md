# App4: Sistema de Generación de Videos Comerciales con IA

## 🎯 Resumen Ejecutivo

**App4** es una herramienta de automatización que transforma la creación de videos comerciales mediante IA, resolviendo tres desafíos clave:

1. **Prompts Estructurados** - Sistema de templates para generar prompts consistentes y de alta calidad
2. **Continuidad Visual** - Tecnología frame-to-frame para mantener coherencia entre clips de 8 segundos
3. **Refinamiento Iterativo** - Proceso automatizado para mejorar acción, emoción y movimiento de cámara

---

## 🎬 Caso de Uso: Comercial LVE Perfume

### Objetivo
Crear un comercial de 30 segundos mostrando una modelo en vestido rojo presentando el perfume LVE.

### Desafío
- Veo 3.1 genera clips de máximo 8 segundos
- Necesitamos 4 clips que se ensamblen perfectamente
- Mantener identidad consistente (modelo + producto)

### Solución
Sistema que usa el **último frame de cada clip** como referencia para el siguiente, garantizando continuidad visual perfecta.

---

## 🏗️ Arquitectura

### Componentes Principales

1. **Prompt Generator** - Genera prompts optimizados desde templates
2. **Continuity Engine** - Mantiene coherencia visual entre clips
3. **Production Orchestrator** - Coordina todo el proceso de producción
4. **Video Assembler** - Ensambla clips en video final

### Flujo de Trabajo

```
1. Usuario crea proyecto desde template
   ↓
2. Sistema genera prompts para cada escena
   ↓
3. Escena 1: Generación inicial (con referencias opcionales)
   ↓
4. Extrae último frame de Escena 1
   ↓
5. Escena 2: Usa último frame como referencia
   ↓
6. Repite proceso para todas las escenas
   ↓
7. Ensambla clips con transiciones suaves
   ↓
8. Video comercial de 30 segundos completado
```

---

## 📊 Características Técnicas

### Sistema de Prompts Estructurados

- **Templates JSON** con variables dinámicas
- **Niveles de refinamiento** (0-3) para mayor detalle
- **Gestión de identidad** para sujetos y productos
- **Especificaciones de cámara** detalladas

### Motor de Continuidad Visual

- **Extracción de frames** con FFmpeg
- **Modo reference images** de Veo 3.1
- **Inyección automática** de último frame
- **Validación de coherencia**

### Orquestador de Producción

- **Gestión asíncrona** de operaciones
- **Monitoreo de progreso** en tiempo real
- **Manejo de errores** y reintentos
- **Base de datos** para proyectos y clips

---

## 🚀 Próximos Pasos

### Para Implementar

1. **Revisar** plan de implementación completo
2. **Decidir** opciones de diseño (DB, storage, etc.)
3. **Crear** estructura del proyecto
4. **Implementar** componentes core
5. **Desarrollar** interfaz de usuario
6. **Probar** con template LVE Perfume

### Decisiones Pendientes

- Base de datos: SQLite vs PostgreSQL
- Almacenamiento: Local vs Cloud (S3/GCS)
- Refinamiento: Automático vs Manual
- Frontend: Continuar con React+Vite vs Next.js

---

## 📁 Archivos Incluidos

- `implementation_plan.md` - Plan técnico detallado con código
- `templates/lve_perfume_commercial.json` - Template de ejemplo completo
- `task.md` - Lista de tareas organizada por fases

---

## ⚡ Ventajas Clave

✅ **Automatización completa** - De idea a video en minutos
✅ **Continuidad perfecta** - Sin cortes visuales abruptos
✅ **Consistencia de marca** - Mantiene identidad visual
✅ **Escalable** - Crea múltiples variaciones fácilmente
✅ **Profesional** - Calidad de producción comercial

---

## 🎯 Resultado Esperado

**Input**: Template JSON con 4 escenas
**Proceso**: 8-20 minutos de generación
**Output**: Video comercial de 30 segundos con:
- Continuidad visual perfecta
- Identidad consistente del sujeto
- Producto destacado apropiadamente
- Calidad cinematográfica 1080p
