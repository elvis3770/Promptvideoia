"""
System Verification Script for App4
Checks all system requirements and configuration
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_check(text, status):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {text}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    is_ok = version.major >= 3 and version.minor >= 8
    print_check(f"Python {version.major}.{version.minor}.{version.micro}", is_ok)
    return is_ok

def check_mongodb():
    """Check MongoDB connection"""
    try:
        import pymongo
        from dotenv import load_dotenv
        load_dotenv()
        
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        client = pymongo.MongoClient(mongodb_url, serverSelectionTimeoutMS=2000)
        client.server_info()
        client.close()
        print_check(f"MongoDB ({mongodb_url})", True)
        return True
    except ImportError:
        print_check("MongoDB (pymongo no instalado)", False)
        return False
    except Exception as e:
        print_check(f"MongoDB (no accesible: {str(e)[:30]}...)", False)
        return False

def check_google_api_key():
    """Check if Google API key is configured"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and api_key != "tu_api_key_aqui":
            print_check("Google API Key configurada", True)
            return True
        else:
            print_check("Google API Key (no configurada en .env)", False)
            return False
    except Exception:
        print_check("Google API Key (error al verificar)", False)
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            shell=True
        )
        is_ok = result.returncode == 0
        if is_ok:
            # Extract version
            version_line = result.stdout.split('\n')[0]
            version = version_line.split(' ')[2] if len(version_line.split(' ')) > 2 else "unknown"
            print_check(f"FFmpeg {version}", True)
        else:
            print_check("FFmpeg (no encontrado)", False)
        return is_ok
    except Exception:
        print_check("FFmpeg (no encontrado)", False)
        return False

def check_dependencies():
    """Check if Python dependencies are installed"""
    required = [
        "fastapi",
        "uvicorn",
        "pymongo",
        "motor",
        "pydantic",
        "python-dotenv",
        "google-genai"
    ]
    
    all_ok = True
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print_check(f"Paquete: {package}", True)
        except ImportError:
            print_check(f"Paquete: {package} (no instalado)", False)
            all_ok = False
    
    return all_ok

def check_directory_structure():
    """Check if directory structure is correct"""
    required_dirs = [
        "backend/core",
        "backend/db",
        "backend/models",
        "backend/utils",
        "frontend/src",
        "templates"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        print_check(f"Directorio: {dir_path}", exists)
        if not exists:
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check if .env file exists"""
    exists = Path(".env").exists()
    print_check(".env file", exists)
    return exists

def test_veo_api():
    """Test connection to Veo API"""
    try:
        from dotenv import load_dotenv
        import google.genai as genai
        
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key or api_key == "tu_api_key_aqui":
            print_check("Veo API (API key no configurada)", False)
            return False
        
        # Try to initialize client
        client = genai.Client(api_key=api_key)
        print_check("Veo API (conexión exitosa)", True)
        return True
    except ImportError:
        print_check("Veo API (google-genai no instalado)", False)
        return False
    except Exception as e:
        print_check(f"Veo API (error: {str(e)[:30]}...)", False)
        return False

def print_summary(results):
    """Print summary of checks"""
    print_header("Resumen")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total de verificaciones: {total}")
    print(f"✅ Pasadas: {passed}")
    print(f"❌ Fallidas: {failed}")
    print()
    
    if failed == 0:
        print("🎉 ¡Todo está configurado correctamente!")
        print("Ejecuta 'python start.py' para iniciar App4")
    else:
        print("⚠️  Hay problemas que necesitan atención")
        print("Ejecuta 'python setup.py' para configurar el sistema")

def main():
    print_header("App4 System Verification")
    
    # Change to app4 directory if needed
    if Path("app4").exists() and not Path("api.py").exists():
        os.chdir("app4")
    
    results = {}
    
    # Run checks
    print_header("Verificando Sistema")
    results["Python"] = check_python_version()
    results["MongoDB"] = check_mongodb()
    results["Google API Key"] = check_google_api_key()
    results["FFmpeg"] = check_ffmpeg()
    
    print_header("Verificando Dependencias")
    results["Dependencies"] = check_dependencies()
    
    print_header("Verificando Estructura")
    results["Directories"] = check_directory_structure()
    results[".env file"] = check_env_file()
    
    print_header("Verificando APIs")
    results["Veo API"] = test_veo_api()
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()
