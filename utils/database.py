import pymysql
import os
import socket
from config import Config

class Database:
    def get_connection(self):
        """Obtener conexión a la base de datos con DEBUG completo"""
        print("=== 🔍 DEBUG AVANZADO - INICIO ===")
        print(f"📡 Conectando a: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
        print(f"👤 Usuario: {Config.MYSQL_USER}")
        print(f"🗄️ Base de datos: {Config.MYSQL_DB}")
        print(f"🔐 Password length: {len(Config.MYSQL_PASSWORD or '')}")
        
        # PRUEBA DE CONECTIVIDAD DE RED
        try:
            print("🌐 Probando conectividad de red...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((Config.MYSQL_HOST, Config.MYSQL_PORT))
            sock.close()
            if result == 0:
                print("✅ Puerto ACCESIBLE - La red funciona")
            else:
                print(f"❌ Puerto INACCESIBLE - Error: {result}")
                print("⚠️ Problema de firewall/red/DNS")
                print("💡 Posibles soluciones:")
                print("   - Verificar que MySQL está en el mismo proyecto")
                print("   - Revisar configuración de red en Railway")
                print("   - Usar mysql-connector-python en lugar de pymysql")
        except Exception as e:
            print(f"❌ Error en prueba de red: {e}")
        
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
            'write_timeout': 10
        }
        
        # CONFIGURACIÓN SSL - PROBAR DIFERENTES OPCIONES
        print("🔐 Configurando SSL...")
        if os.getenv('RAILWAY_ENV') or Config.MYSQL_HOST != 'localhost':
            # Opción 1: SSL simple
            connection_config['ssl'] = {'ssl': True}
            print("   ✅ SSL configurado (modo simple)")
            
            # Opción 2: Probar sin SSL temporalmente
            # print("   ⚠️ SSL desactivado temporalmente para pruebas")
        
        print("=== 🔍 DEBUG AVANZADO - FIN ===")
        
        try:
            print("🔄 Intentando conexión MySQL...")
            connection = pymysql.connect(**connection_config)
            print("✅ CONEXIÓN EXITOSA a MySQL!")
            return connection
        except pymysql.err.OperationalError as e:
            print(f"❌ Error de conexión MySQL: {e}")
            print(f"🔍 Detalles:")
            print(f"   - Host: {Config.MYSQL_HOST}")
            print(f"   - Puerto: {Config.MYSQL_PORT}")
            print(f"   - Usuario: {Config.MYSQL_USER}")
            print(f"   - DB: {Config.MYSQL_DB}")
            print("💡 Soluciones sugeridas:")
            print("   1. Verificar que la BD está funcionando en Railway")
            print("   2. Probar con mysql-connector-python")
            print("   3. Revisar variables de entorno")
            print("   4. Recrear el servicio completo")
            raise e
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            raise e

    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Ejecutar consulta en la base de datos"""
        print(f"📝 Ejecutando query: {query[:100]}...")
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                
                if fetch:
                    result = cursor.fetchall()
                    print(f"📊 Resultados obtenidos: {len(result)} filas")
                elif fetch_one:
                    result = cursor.fetchone()
                    print("📊 Resultado único obtenido")
                else:
                    result = cursor.lastrowid
                    print(f"📝 ID generado: {result}")
                
                if not fetch and not fetch_one:
                    connection.commit()
                    print("💾 Cambios guardados en BD")
                
                return result
        except Exception as e:
            connection.rollback()
            print(f"❌ Error en consulta MySQL: {e}")
            raise e
        finally:
            connection.close()
            print("🔌 Conexión cerrada")