"""
Start Script for App4
Starts both backend and frontend servers
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Global process references
backend_process = None
frontend_process = None

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(text):
    print(f">> {text}")

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def check_mongodb():
    """Check if MongoDB is running"""
    print_step("Verificando MongoDB...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.server_info()
        client.close()
        print_success("MongoDB está corriendo")
        return True
    except Exception:
        print_error("MongoDB no está corriendo")
        print("  Inicia MongoDB antes de ejecutar este script")
        return False

def start_backend():
    """Start the FastAPI backend"""
    global backend_process
    print_step("Iniciando backend...")
    
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--port", "8003", "--host", "127.0.0.1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)  # Give it time to start
        
        if backend_process.poll() is None:
            print_success("Backend iniciado en http://localhost:8003")
            return True
        else:
            print_error("Error al iniciar backend")
            return False
    except Exception as e:
        print_error(f"Error al iniciar backend: {e}")
        return False

def start_frontend():
    """Start the Vite frontend"""
    global frontend_process
    print_step("Iniciando frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_error("Directorio frontend no encontrado")
        return False
    
    try:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=True
        )
        time.sleep(3)  # Give it time to start
        
        if frontend_process.poll() is None:
            print_success("Frontend iniciado en http://localhost:5174")
            return True
        else:
            print_error("Error al iniciar frontend")
            return False
    except Exception as e:
        print_error(f"Error al iniciar frontend: {e}")
        return False

def cleanup():
    """Cleanup processes on exit"""
    global backend_process, frontend_process
    
    print("\n")
    print_step("Cerrando servicios...")
    
    if backend_process:
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
            print_success("Backend cerrado")
        except subprocess.TimeoutExpired:
            backend_process.kill()
            print_success("Backend forzado a cerrar")
    
    if frontend_process:
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
            print_success("Frontend cerrado")
        except subprocess.TimeoutExpired:
            frontend_process.kill()
            print_success("Frontend forzado a cerrar")
    
    print("\n[BYE] App4 cerrado")

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    cleanup()
    sys.exit(0)

def main():
    print_header("App4 Start - Iniciando Sistema")
    
    # Change to app4 directory if needed
    if Path("app4").exists() and not Path("api.py").exists():
        os.chdir("app4")
        print_step("Cambiando al directorio app4")
    
    # Check MongoDB
    if not check_mongodb():
        return
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start backend
    if not start_backend():
        cleanup()
        return
    
    # Start frontend
    if not start_frontend():
        cleanup()
        return
    
    # Print access info
    print_header("App4 está corriendo!")
    print("  Backend:  http://localhost:8003")
    print("  Frontend: http://localhost:5174")
    print("  API Docs: http://localhost:8003/docs")
    print()
    print("Presiona Ctrl+C para detener los servicios")
    print()
    
    # Keep running until Ctrl+C
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            if backend_process.poll() is not None:
                print_error("Backend se detuvo inesperadamente")
                break
            if frontend_process.poll() is not None:
                print_error("Frontend se detuvo inesperadamente")
                break
    except KeyboardInterrupt:
        pass
    
    cleanup()

if __name__ == "__main__":
    main()
