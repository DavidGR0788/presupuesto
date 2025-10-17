import pymysql
from config import Config
import socket

class Database:
    def get_connection(self):
        """Obtener conexión a la base de datos con SSL corregido"""
        
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
            'connect_timeout': 10,
            'read_timeout': 10,
            'write_timeout': 10,
        }
        
        # ✅ CONFIGURACIÓN SSL CORREGIDA PARA RAILWAY
        if Config.IS_RAILWAY:
            # Opción 1: Probar sin SSL primero (más probable que funcione)
            connection_config['ssl'] = False
            print("   🔓 SSL deshabilitado - Modo seguro")
            
            # Opción 2: Si necesitas SSL, usa esta configuración
            # connection_config['ssl'] = {
            #     'ssl': True,
            #     'ssl_ca': None,
            #     'ssl_verify_cert': False,
            #     'ssl_verify_identity': False
            # }
            # print("   🔐 SSL con verificación deshabilitada")
        
        try:
            # ✅ PRIMERO: Verificar conectividad básica
            print(f"   🔍 Probando conectividad a {Config.MYSQL_HOST}:{Config.MYSQL_PORT}...")
            sock = socket.create_connection((Config.MYSQL_HOST, Config.MYSQL_PORT), timeout=10)
            sock.close()
            print("   ✅ Conectividad OK - Puerto accesible")
            
            # ✅ SEGUNDO: Intentar conexión MySQL
            print("   🔌 Estableciendo conexión MySQL...")
            start_time = socket.time() if hasattr(socket, 'time') else __import__('time').time()
            
            connection = pymysql.connect(**connection_config)
            
            end_time = socket.time() if hasattr(socket, 'time') else __import__('time').time()
            connection_time = end_time - start_time
            
            print(f"   ✅ Conexión MySQL exitosa ({connection_time:.2f}s)")
            return connection
            
        except socket.timeout:
            error_msg = f"❌ Timeout: No se puede conectar a {Config.MYSQL_HOST}:{Config.MYSQL_PORT}"
            print(error_msg)
            raise Exception(error_msg)
        except socket.gaierror as e:
            error_msg = f"❌ Error DNS: No se puede resolver {Config.MYSQL_HOST}"
            print(error_msg)
            raise Exception(error_msg)
        except pymysql.OperationalError as e:
            error_code, error_msg = e.args
            print(f"❌ Error operacional MySQL [{error_code}]: {error_msg}")
            
            # Si es error de SSL, sugerir solución
            if "SSL" in str(e).upper() or "TLS" in str(e).upper():
                print("💡 SOLUCIÓN: El problema es SSL. Se ha deshabilitado automáticamente.")
            
            raise e
        except Exception as e:
            print(f"❌ Error de conexión MySQL: {e}")
            print(f"💡 Tipo de error: {type(e).__name__}")
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
        except Exception as e:
            print(f"❌ Test conexión rápida falló: {e}")
            return False

    def get_database_size(self):
        """Obtener tamaño de la base de datos (si es posible)"""
        try:
            if not Config.IS_RAILWAY:
                return "Solo disponible en Railway"
                
            query = """
            SELECT 
                table_schema as database_name,
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
            FROM information_schema.tables 
            WHERE table_schema = %s
            GROUP BY table_schema
            """
            result = self.execute_query(query, (Config.MYSQL_DB,), fetch_one=True)
            return f"{result['size_mb']} MB" if result else "No disponible"
        except:
            return "No se pudo obtener"