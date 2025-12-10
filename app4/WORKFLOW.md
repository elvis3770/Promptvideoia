# Flujo de Trabajo Detallado

## 🎬 Escena 1: Producto Principal

### Paso 1: Subir Imagen del Producto
```
Usuario arrastra imagen: "Mujer con 4 perfumes en mesa"
         ↓
Gemini analiza automáticamente:
- Posición: "Mujer sentada, 4 perfumes frente a ella"
- Colores: ["negro", "dorado", "morado", "blanco"]
- Iluminación: "Suave, de estudio"
- Mood: "Elegante, sofisticado"
         ↓
Genera prompt base automáticamente
```

### Paso 2: Escribir Acción y Diálogo
```
Campo Prompt: "La mujer muestra el perfume negro"
Campo Diálogo: "Este es el aroma de la elegancia, che"
Campo Emoción: "Confiada"
```

### Paso 3: Optimizar con IA
```
Click "Optimizar con IA"
         ↓
Gemini combina:
- Contexto visual (lo que vio en la imagen)
- Acción del usuario
- Diálogo
- Emoción
         ↓
Resultado optimizado:
"Elegant woman seated at glossy table with 4 luxury perfume bottles 
(black, gold, purple, white) arranged in front, soft studio lighting, 
medium shot. Woman gracefully reaches for and picks up the black perfume 
bottle, holds it up to camera with confident gesture, speaks directly 
to viewer: 'Este es el aroma de la elegancia, che' with sophisticated 
Argentine accent. Smooth camera push-in to close-up of bottle as she speaks. 
Maintain elegant, luxurious atmosphere throughout."
```

### Paso 4: Usar en Generador de Video
```
Tomas:
- Prompt optimizado ✅
- Imagen original ✅
         ↓
Los usas en tu generador externo (Veo, Runway, etc.)
```

## 🎬 Escenas 2+: Continuidad Visual

### Paso 1: Subir Último Frame
```
Usuario arrastra último frame de Escena 1
         ↓
Gemini analiza para continuidad:
- Posición final del sujeto
- Iluminación
- Colores
- Mood
         ↓
Sugiere cómo empezar Escena 2:
"Start with close-up of perfume bottle in hand, 
same elegant lighting, maintain sophisticated mood"
         ↓
Se agrega automáticamente:
[CONTINUITY: ...] + tu prompt
```

### Paso 2: Escribir Nueva Acción
```
Campo Prompt: "La mujer rocía el perfume"
         ↓
Prompt completo:
"[CONTINUITY: close-up bottle in hand, elegant lighting] 
La mujer rocía el perfume"
```

### Paso 3: Optimizar
```
Click "Optimizar con IA"
         ↓
Gemini optimiza manteniendo continuidad visual
```

## 💡 Ejemplo Completo: Comercial de Perfume

### Escena 1
**Imagen:** Mujer con 4 perfumes  
**Acción:** "Muestra perfume negro"  
**Diálogo:** "Este es el aroma de la elegancia"  
**Resultado:** Prompt que describe imagen + acción + diálogo

### Escena 2  
**Frame anterior:** Último frame de Escena 1  
**Acción:** "Rocía el perfume"  
**Resultado:** Prompt con continuidad visual + nueva acción

### Escena 3
**Frame anterior:** Último frame de Escena 2  
**Acción:** "Sonríe a cámara"  
**Resultado:** Prompt con continuidad + cierre elegante
