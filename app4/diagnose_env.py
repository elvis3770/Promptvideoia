"""
Script para verificar la configuración del .env y diagnosticar el error 500
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("DIAGNÓSTICO DE CONFIGURACIÓN")
print("=" * 60)

# Load .env
load_dotenv()

# Check Gemini API Key
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print(f"✅ GEMINI_API_KEY encontrada: {gemini_key[:10]}...")
else:
    print("❌ GEMINI_API_KEY NO encontrada en .env")
    print("   Necesitas agregar: GEMINI_API_KEY=tu_api_key")

# Check WebAI settings
use_local = os.getenv("USE_LOCAL_GEMINI", "false").lower() == "true"
webai_url = os.getenv("WEBAI_API_BASE_URL", "http://localhost:6969/v1")

print(f"\n{'✅' if use_local else '⚠️'} USE_LOCAL_GEMINI: {use_local}")
print(f"   WEBAI_API_BASE_URL: {webai_url}")

# Test Gemini API
if gemini_key:
    print("\n" + "=" * 60)
    print("PROBANDO CONEXIÓN CON GEMINI API")
    print("=" * 60)
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        
        # Try with gemini-2.5-flash
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say 'API works'")
        
        print("✅ Conexión exitosa con Gemini API")
        print(f"   Modelo: gemini-2.5-flash")
        print(f"   Respuesta: {response.text[:50]}...")
        
    except Exception as e:
        print(f"❌ Error al conectar con Gemini API:")
        print(f"   {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Verifica que GEMINI_API_KEY sea correcta")
        print("2. Verifica que tengas cuota disponible")
        print("3. Intenta con otra API key")

print("\n" + "=" * 60)
print("CONFIGURACIÓN RECOMENDADA PARA .env")
print("=" * 60)
print("""
# API Keys
GEMINI_API_KEY=tu_api_key_aqui

# WebAI (para optimización de texto gratis)
USE_LOCAL_GEMINI=true
WEBAI_API_BASE_URL=http://localhost:6969/v1

# MongoDB (opcional)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=prompt_comercial

# Puertos
BACKEND_PORT=8003
FRONTEND_PORT=5174
""")
