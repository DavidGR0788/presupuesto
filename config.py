import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Configuración para Railway - SIN valores por defecto locales
    MYSQL_HOST = os.getenv('MYSQLHOST')  # Railway proveerá este valor
    MYSQL_USER = os.getenv('MYSQLUSER')  # Railway proveerá este valor
    MYSQL_PASSWORD = os.getenv('MYSQLPASSWORD')  # Railway proveerá este valor
    MYSQL_DB = os.getenv('MYSQLDATABASE')  # Railway proveerá este valor
    MYSQL_PORT = int(os.getenv('MYSQLPORT', 3306))  # Solo puerto tiene valor por defecto
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'presupuesto_secret_key_2025')
    
    # Configuración de sesión - NO permanente (se cierra al cerrar navegador)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    
    # Método de debug para verificar configuración
    @classmethod
    def print_debug(cls):
        print("=== 🚨 CONFIG DEBUG ===")
        print(f"MYSQL_HOST: '{cls.MYSQL_HOST}'")
        print(f"MYSQL_USER: '{cls.MYSQL_USER}'")
        print(f"MYSQL_DB: '{cls.MYSQL_DB}'")
        print(f"MYSQL_PORT: {cls.MYSQL_PORT}")
        print(f"MYSQL_PASSWORD length: {len(cls.MYSQL_PASSWORD or '')}")
        print("=== 🚨 CONFIG DEBUG END ===")

# Debug inicial
if __name__ == "__main__":
    Config.print_debug()