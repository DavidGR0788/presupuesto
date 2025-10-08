import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Configuración para Railway - usa los nombres EXACTOS de Railway
    MYSQL_HOST = os.getenv('MYSQLHOST', 'localhost')  # Railway usa MYSQLHOST (sin guión)
    MYSQL_USER = os.getenv('MYSQLUSER', 'root')       # Railway usa MYSQLUSER (sin guión)
    MYSQL_PASSWORD = os.getenv('MYSQLPASSWORD', '')   # Railway usa MYSQLPASSWORD (sin guión)
    MYSQL_DB = os.getenv('MYSQLDATABASE', 'presupuesto_db')  # Railway usa MYSQLDATABASE
    MYSQL_PORT = int(os.getenv('MYSQLPORT', 3306))    # Railway usa MYSQLPORT (sin guión)
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'Unpocodetodo1007$')
    
    # Configuración de sesión - NO permanente (se cierra al cerrar navegador)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)