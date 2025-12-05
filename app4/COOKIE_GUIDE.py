"""
Quick guide: Extract Gemini Cookies Manually
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║  GUÍA RÁPIDA: Extraer Cookies de Gemini (Manual)            ║
╔══════════════════════════════════════════════════════════════╗

PASO 1: Abrir Gemini
   → https://gemini.google.com/app
   → Asegúrate de estar logueado

PASO 2: Abrir DevTools
   → Presiona F12 (o Ctrl+Shift+I)
   → Ve a la pestaña "Application" (o "Aplicación")

PASO 3: Encontrar Cookies
   → En el panel izquierdo: Storage → Cookies
   → Click en "https://gemini.google.com"

PASO 4: Copiar estas cookies (IMPORTANTES):
   
   1. __Secure-1PSID
      → Click en la cookie
      → Copia el "Value" completo
   
   2. __Secure-1PSIDTS (opcional pero recomendado)
      → Click en la cookie
      → Copia el "Value" completo

PASO 5: Agregar al .env de WebAI-to-API

   Edita: c:\\Users\\Admin\\WebAI-to-API-master\\WebAI-to-API-master\\.env
   
   Agrega estas líneas:
   
   # Gemini Cookie Authentication
   GEMINI_COOKIE_1PSID=tu_valor_de_1PSID_aqui
   GEMINI_COOKIE_1PSIDTS=tu_valor_de_1PSIDTS_aqui
   USE_G4F=false

PASO 6: Reiniciar servidor (o usar switch en runtime)
   
   Opción A - Switch en runtime (MÁS RÁPIDO):
      → En la terminal donde corre el servidor
      → Presiona: 1 + Enter
      → Verás: "[Controller] Switching to 'cookie' mode..."
   
   Opción B - Reiniciar:
      → Ctrl+C para detener
      → python src\\run.py para iniciar

VERIFICACIÓN:
   
   Deberías ver en los logs:
   ✅ Cookie authentication mode enabled
   ✅ Gemini session active

PROBAR:
   
   curl -X POST http://localhost:6969/v1/chat/completions \\
     -H "Content-Type: application/json" \\
     -d '{"model":"gemini-2.0-flash-exp","messages":[{"role":"user","content":"test"}]}'

╚══════════════════════════════════════════════════════════════╝

IMPORTANTE:
- Mantén la pestaña de Gemini ABIERTA mientras uses WebAI-to-API
- Las cookies expiran (~24-48h), tendrás que renovarlas
- Si ves errores de autenticación, repite este proceso

""")
