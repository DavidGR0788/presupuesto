import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Configuración para PostgreSQL en Render
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    
    # Variables individuales para compatibilidad (si las necesitas)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'presupuesto')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-super-secreta-muy-larga-2025-presupuesto-app')
    
    # Configuración de sesión - NO permanente (se cierra al cerrar navegador)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)