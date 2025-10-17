import pymysql
from config import Config
import socket

class Database:
    def get_connection(self):
        """Obtener conexión a la base de datos con timeouts mejorados"""
        
        # Mostrar entorno actual
        if Config.IS_RAILWAY:
            print("🟢 Database: Conectando a Railway MySQL")
        else:
            print("🔵 Database: Conectando a Local MySQL")
        
        connection_config = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DB,
            'port': Config.MYSQL_PORT,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
            'connect_timeout': 5,      # ✅ Reducido a 5 segundos
            'read_timeout': 10,        # ✅ Agregado timeout de lectura
            'write_timeout': 10,       # ✅ Agregado timeout de escritura
        }
        
        # ✅ Configuración SSL solo para Railway
        if Config.IS_RAILWAY:
            connection_config['ssl'] = {'ssl': True}
            print("   🔐 SSL habilitado para Railway")
        
        try:
            # ✅ PRIMERO: Verificar conectividad básica
            print(f"   🔍 Probando conectividad a {Config.MYSQL_HOST}:{Config.MYSQL_PORT}...")
            sock = socket.create_connection((Config.MYSQL_HOST, Config.MYSQL_PORT), timeout=5)
            sock.close()
            print("   ✅ Conectividad OK - Puerto accesible")
            
            # ✅ SEGUNDO: Intentar conexión MySQL
            print("   🔌 Estableciendo conexión MySQL...")
            connection = pymysql.connect(**connection_config)
            print("   ✅ Conexión MySQL exitosa")
            return connection
            
        except socket.timeout:
            error_msg = f"❌ Timeout: No se puede conectar a {Config.MYSQL_HOST}:{Config.MYSQL_PORT}"
            print(error_msg)
            raise Exception(error_msg)
        except socket.gaierror as e:
            error_msg = f"❌ Error DNS: No se puede resolver {Config.MYSQL_HOST}"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            print(f"❌ Error de conexión MySQL: {e}")
            raise e

    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Ejecutar consulta en la base de datos con manejo mejorado de errores"""
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                
                if fetch:
                    result = cursor.fetchall()
                elif fetch_one:
                    result = cursor.fetchone()
                else:
                    result = cursor.lastrowid
                    connection.commit()
                
                return result
        except Exception as e:
            connection.rollback()
            print(f"❌ Error en consulta: {e}")
            raise e
        finally:
            connection.close()

    def test_connection_quick(self):
        """Método rápido para testear conexión sin bloquear"""
        try:
            conn = self.get_connection()
            conn.close()
            return True
        except:
            return False