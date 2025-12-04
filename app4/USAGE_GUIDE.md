# Guía de Uso - App4 Video Commercial Generator

Esta guía te llevará paso a paso a través del proceso completo de crear un video comercial con App4.

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Crear un Proyecto](#crear-un-proyecto)
3. [Iniciar la Producción](#iniciar-la-producción)
4. [Monitorear el Progreso](#monitorear-el-progreso)
5. [Ver y Descargar Resultados](#ver-y-descargar-resultados)
6. [Mejores Prácticas](#mejores-prácticas)
7. [Ejemplos Prácticos](#ejemplos-prácticos)

## Configuración Inicial

### Paso 1: Verificar Requisitos

Antes de comenzar, asegúrate de tener:
- Python 3.8 o superior
- Node.js y npm
- MongoDB (local o Atlas)
- FFmpeg
- API key de Google Veo 3.1

### Paso 2: Ejecutar Setup

```bash
cd app4
python setup.py
```

Este script:
- Instala todas las dependencias
- Verifica que MongoDB y FFmpeg estén disponibles
- Crea el archivo `.env`

### Paso 3: Configurar API Key

Edita el archivo `.env` y agrega tu API key:

```env
MONGODB_URL=mongodb://localhost:27017
GOOGLE_API_KEY=tu_api_key_real_aqui
```

### Paso 4: Verificar Sistema

```bash
python verify_system.py
```

Deberías ver ✅ en todas las verificaciones.

### Paso 5: Iniciar Aplicación

```bash
python start.py
```

Abre tu navegador en http://localhost:5174

## Crear un Proyecto

### Opción A: Usar el Editor Visual (Recomendado)

1. **Acceder al Editor**
   - Haz clic en "New Project" en el Dashboard
   - Se abrirá el Editor de Templates

2. **Información Básica**
   - **Nombre**: Dale un nombre descriptivo a tu proyecto
   - **Duración**: Establece la duración total deseada (15-60 segundos)
   - **Descripción**: Breve descripción del comercial

3. **Definir el Sujeto**
   - **Tipo**: persona, producto, animal, lugar, etc.
   - **Descripción**: Descripción detallada en inglés
   - Ejemplo: "elegant woman with long dark hair wearing red dress"

4. **Información del Producto**
   - **Nombre**: Nombre del producto o marca
   - **Categoría**: perfume, tecnología, alimentos, etc.

5. **Guías de Marca**
   - **Mood**: elegante, moderno, juvenil, etc.
   - **Estilo**: minimalista, cinematográfico, etc.

6. **Agregar Escenas**
   - Haz clic en "Agregar Escena"
   - Para cada escena define:
     - **Nombre**: Identificador de la escena
     - **Duración**: 5-15 segundos
     - **Prompt**: Descripción detallada en inglés de lo que sucede
     - **Emoción**: neutral, alegría, misterio, etc.
     - **Movimiento de Cámara**: estática, pan, dolly, etc.
     - **Iluminación**: natural, dramática, golden hour, etc.

7. **Guardar Proyecto**
   - Haz clic en "Crear Proyecto"
   - El proyecto se guardará en la base de datos

### Opción B: Usar un Template Existente

1. **Cargar Template**
   - En el Editor, haz clic en "Cargar JSON"
   - Selecciona uno de los templates en `templates/`:
     - `simple_product_showcase.json` - 2 escenas, 15s
     - `brand_story.json` - 3 escenas, 22s
     - `lve_perfume_commercial.json` - 4 escenas, 30s

2. **Personalizar**
   - Modifica los campos según tu necesidad
   - Cambia los prompts para tu producto
   - Ajusta duraciones y configuraciones

3. **Guardar**
   - Haz clic en "Crear Proyecto"

## Iniciar la Producción

1. **Desde el Dashboard**
   - Encuentra tu proyecto en la lista
   - Haz clic en "Start Production"
   - Confirma que quieres iniciar

2. **Navegación Automática**
   - Serás redirigido al Monitor de Producción
   - El proceso comenzará automáticamente

3. **Modo Automático**
   - Por defecto, todas las escenas se generan automáticamente
   - No se requiere intervención manual

## Monitorear el Progreso

### Vista del Monitor

El Monitor de Producción muestra:

1. **Estado General**
   - RUNNING: Producción en progreso
   - COMPLETED: Producción finalizada
   - FAILED: Error en la producción

2. **Progreso de Escenas**
   - Barra de progreso general
   - Estado de cada escena individual:
     - ⏱️ PENDING: Esperando
     - ⚙️ GENERATING: Generando
     - ✅ COMPLETED: Completada
     - ❌ FAILED: Error

3. **Información de Tiempo**
   - Hora de inicio
   - Escena actual
   - Progreso total

### Tiempos Estimados

- **Escena individual**: 2-5 minutos
- **Proyecto de 2 escenas**: 4-10 minutos
- **Proyecto de 3 escenas**: 6-15 minutos
- **Proyecto de 4 escenas**: 8-20 minutos

### Actualización en Tiempo Real

El monitor se actualiza automáticamente cada 5 segundos.

## Ver y Descargar Resultados

### Acceder al Visor

1. **Desde el Dashboard**
   - Encuentra tu proyecto completado
   - Haz clic en "View"

2. **Desde el Monitor**
   - Cuando la producción termine
   - Haz clic en "Ver Proyecto"

### Pestaña "Video Final"

- **Reproductor**: Video completo ensamblado
- **Información**: Duración, resolución, formato
- **Descargar**: Botón para descargar el video final

### Pestaña "Clips Individuales"

- **Lista de Clips**: Todos los clips generados
- **Reproducción**: Cada clip se puede reproducir
- **Información**: Prompt usado, duración, ID de Veo
- **Descargar**: Cada clip se puede descargar individualmente

### Detalles del Proyecto

- Información del sujeto
- Información del producto
- Guías de marca utilizadas

## Mejores Prácticas

### Escribir Buenos Prompts

✅ **Hacer:**
- Ser específico y detallado
- Usar inglés para mejores resultados
- Describir iluminación, ángulos, movimientos
- Incluir emociones y atmósfera
- Mencionar calidad (4K, cinematic, professional)

❌ **Evitar:**
- Prompts muy cortos o vagos
- Cambios drásticos entre escenas
- Demasiados elementos en una escena
- Instrucciones contradictorias

### Ejemplos de Buenos Prompts

**Producto Tecnológico:**
```
sleek black smartphone rotating slowly on white pedestal, 
studio lighting with blue accent lights, minimalist 
background, product photography style, 4K quality, 
professional commercial aesthetic
```

**Persona:**
```
confident businesswoman walking through modern office, 
natural window lighting, medium tracking shot following 
from side, professional attire, warm color grading, 
cinematic quality
```

**Alimentos:**
```
close-up of chef's hands carefully plating gourmet dish, 
soft overhead lighting, steam rising gently, shallow 
depth of field, warm tones, food photography style, 
appetizing presentation
```

### Continuidad Visual

Para mantener coherencia entre escenas:

1. **Sujeto Consistente**: Usa la misma descripción del sujeto
2. **Iluminación Similar**: Mantén el estilo de iluminación
3. **Paleta de Colores**: Usa colores consistentes
4. **Transiciones Lógicas**: Las escenas deben fluir naturalmente

### Duración de Escenas

- **Mínimo**: 5 segundos
- **Óptimo**: 7-8 segundos
- **Máximo**: 15 segundos
- **Total recomendado**: 15-30 segundos

## Ejemplos Prácticos

### Ejemplo 1: Comercial de Perfume (30s)

**Escena 1** (8s): Entrada elegante
```
elegant woman in red dress walking through luxury hotel 
lobby, warm golden hour sunlight, smooth tracking shot, 
confident stride, cinematic quality
```

**Escena 2** (8s): Revelación del producto
```
woman turns gracefully revealing perfume bottle in hand, 
slow zoom to close-up, mysterious smile, soft key lighting, 
product highlighted, elegant presentation
```

**Escena 3** (7s): Aplicación
```
close-up of woman applying perfume to neck, eyes closed 
in pleasure, soft diffused lighting, sensual moment, 
luxury aesthetic
```

**Escena 4** (7s): Final poderoso
```
woman with confident gaze holding perfume at chest level, 
dramatic lighting, slow pull back, elegant composition, 
brand reveal
```

### Ejemplo 2: Showcase de Producto (15s)

**Escena 1** (7.5s): Producto en rotación
```
modern smartphone rotating on white pedestal, studio 
lighting with blue accents, minimalist background, 
product photography, 4K quality
```

**Escena 2** (7.5s): Funcionalidad
```
close-up of smartphone screen with vibrant interface, 
finger swiping smoothly, soft studio lighting, modern 
aesthetic, professional product video
```

### Ejemplo 3: Historia de Marca - Café (22s)

**Escena 1** (7s): Los granos
```
coffee beans being poured into wooden bowl, warm morning 
sunlight, rustic table, steam rising, artisanal aesthetic, 
shallow depth of field
```

**Escena 2** (7.5s): El arte
```
barista creating latte art, focused expression, cozy 
coffee shop interior, warm ambient lighting, professional 
craftsmanship, medium shot
```

**Escena 3** (7.5s): La experiencia
```
customer holding latte with perfect foam art, sitting 
by window, natural light, steam rising, content smile, 
cozy atmosphere, inviting scene
```

## Solución de Problemas Comunes

### La producción falla

1. Verifica tu API key en `.env`
2. Revisa que MongoDB esté corriendo
3. Chequea los logs en el Monitor
4. Simplifica los prompts si son muy complejos

### El video final no se ensambla

1. Verifica que FFmpeg esté instalado
2. Asegúrate de que todos los clips se generaron
3. Revisa los permisos de escritura en el directorio

### Los clips no tienen continuidad

1. Usa descripciones consistentes del sujeto
2. Mantén la misma paleta de colores
3. Evita cambios drásticos de iluminación
4. Asegúrate de que `continuity_mode` esté configurado

## Consejos Avanzados

### Usar Imágenes de Referencia

Puedes agregar imágenes de referencia en el JSON:

```json
"reference_images": [
  "/path/to/reference1.jpg",
  "/path/to/reference2.jpg"
]
```

### Ajustar Niveles de Refinamiento

En el código, puedes ajustar el nivel de refinamiento de prompts (0-3):

```python
prompt = generator.generate_prompt(scene, refinement_level=3)
```

### Modo Manual

Para aprobar cada escena manualmente:

```python
result = await orchestrator.produce_commercial(
    project_template=template,
    auto_mode=False
)
```

## Recursos Adicionales

- **API Docs**: http://localhost:8003/docs
- **Google Veo 3.1**: https://ai.google.dev/gemini-api/docs/veo
- **Templates de Ejemplo**: `templates/` directory
- **Código Fuente**: `backend/` y `frontend/` directories

---

¿Tienes preguntas? Revisa la sección de Solución de Problemas en el README.md
