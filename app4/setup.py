"""
Setup Script for App4
Installs dependencies and configures the environment
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(text):
    print(f"➤ {text}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def check_python_version():
    """Check if Python version is 3.8+"""
    print_step("Verificando versión de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    else:
        print_error(f"Python 3.8+ requerido. Versión actual: {version.major}.{version.minor}")
        return False

def install_backend_dependencies():
    """Install Python dependencies"""
    print_step("Instalando dependencias de Python...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_success("Dependencias de Python instaladas")
        return True
    except subprocess.CalledProcessError:
        print_error("Error al instalar dependencias de Python")
        return False

def install_frontend_dependencies():
    """Install npm dependencies"""
    print_step("Instalando dependencias de frontend...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print_warning("Directorio frontend no encontrado")
        return False
    
    try:
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, shell=True)
        print_success("Dependencias de frontend instaladas")
        return True
    except subprocess.CalledProcessError:
        print_error("Error al instalar dependencias de frontend")
        print_warning("Asegúrate de tener Node.js y npm instalados")
        return False
    except FileNotFoundError:
        print_error("npm no encontrado")
        print_warning("Instala Node.js desde: https://nodejs.org/")
        return False

def check_mongodb():
    """Check if MongoDB is accessible"""
    print_step("Verificando MongoDB...")
    try:
        import pymongo
        # Try to connect
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.server_info()
        print_success("MongoDB está corriendo")
        client.close()
        return True
    except Exception:
        print_warning("MongoDB no está corriendo o no es accesible")
        print("  Opciones:")
        print("  1. Instalar MongoDB local: https://www.mongodb.com/try/download/community")
        print("  2. Usar MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print_step("Verificando FFmpeg...")
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print_success("FFmpeg está instalado")
            return True
        else:
            print_warning("FFmpeg no encontrado")
            print("  Instala FFmpeg desde: https://ffmpeg.org/download.html")
            return False
    except FileNotFoundError:
        print_warning("FFmpeg no encontrado")
        print("  Instala FFmpeg desde: https://ffmpeg.org/download.html")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_step("Configurando archivo .env...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print_warning(".env ya existe, no se sobrescribirá")
        return True
    
    if not env_example.exists():
        print_error(".env.example no encontrado")
        return False
    
    # Copy .env.example to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print_success("Archivo .env creado")
    print_warning("⚠️  IMPORTANTE: Edita .env y configura tu GOOGLE_API_KEY")
    return True

def print_checklist():
    """Print configuration checklist"""
    print_header("Checklist de Configuración")
    
    print("Antes de ejecutar App4, asegúrate de:")
    print()
    print("  [ ] MongoDB está corriendo (local o Atlas)")
    print("  [ ] GOOGLE_API_KEY configurada en .env")
    print("  [ ] FFmpeg instalado y en PATH")
    print("  [ ] Dependencias de Python instaladas")
    print("  [ ] Dependencias de frontend instaladas")
    print()
    print("Para iniciar el sistema, ejecuta:")
    print("  python start.py")
    print()

def main():
    print_header("App4 Setup - Instalación y Configuración")
    
    # Change to app4 directory if needed
    if Path("app4").exists() and not Path("requirements.txt").exists():
        os.chdir("app4")
        print_step("Cambiando al directorio app4")
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
        return
    
    # Install backend dependencies
    if not install_backend_dependencies():
        success = False
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        success = False
    
    # Check MongoDB
    check_mongodb()
    
    # Check FFmpeg
    check_ffmpeg()
    
    # Create .env file
    create_env_file()
    
    # Print checklist
    print_checklist()
    
    if success:
        print_success("Setup completado!")
    else:
        print_warning("Setup completado con advertencias")

if __name__ == "__main__":
    main()
