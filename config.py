import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # ✅ DETECCIÓN AUTOMÁTICA DE ENTORNO
    IS_RAILWAY = 'RAILWAY_ENVIRONMENT' in os.environ or 'PORT' in os.environ
    
    if IS_RAILWAY:
        # ✅ CONFIGURACIÓN PARA RAILWAY
        print("🟢 Config: Modo Railway detectado")
        MYSQL_HOST = os.getenv('MYSQLHOST', 'localhost')
        MYSQL_USER = os.getenv('MYSQLUSER', 'root')
        MYSQL_PASSWORD = os.getenv('MYSQLPASSWORD', '')
        MYSQL_DB = os.getenv('MYSQLDATABASE', 'presupuesto_personal')
        MYSQL_PORT = int(os.getenv('MYSQLPORT', 3306))
    else:
        # ✅ CONFIGURACIÓN PARA LOCAL (XAMPP)
        print("🔵 Config: Modo Local detectado")
        MYSQL_HOST = 'localhost'
        MYSQL_USER = 'root'
        MYSQL_PASSWORD = ''  # Vacío para XAMPP por defecto
        MYSQL_DB = 'presupuesto_personal'
        MYSQL_PORT = 3306
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'presupuesto_secret_key_2025')
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    
    # Método de debug para verificar configuración
    @classmethod
    def print_debug(cls):
        print("=== 🔍 CONFIGURACIÓN ACTUAL ===")
        print(f"Entorno: {'Railway' if cls.IS_RAILWAY else 'Local'}")
        print(f"MYSQL_HOST: '{cls.MYSQL_HOST}'")
        print(f"MYSQL_USER: '{cls.MYSQL_USER}'")
        print(f"MYSQL_DB: '{cls.MYSQL_DB}'")
        print(f"MYSQL_PORT: {cls.MYSQL_PORT}")
        print(f"MYSQL_PASSWORD length: {len(cls.MYSQL_PASSWORD or '')}")
        print("=== ✅ CONFIGURACIÓN LISTA ===\n")

# Debug inicial
if __name__ == "__main__":
    Config.print_debug()