import pymysql
from config import Config

class Database:
    def get_connection(self):
        """Obtener conexión a la base de datos - Versión simplificada"""
        
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
            'connect_timeout': 10
        }
        
        # ✅ Configuración SSL solo para Railway
        if Config.IS_RAILWAY:
            connection_config['ssl'] = {'ssl': True}
            print("   🔐 SSL habilitado para Railway")
        
        try:
            connection = pymysql.connect(**connection_config)
            print("✅ Conexión MySQL exitosa")
            return connection
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            raise e

    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Ejecutar consulta en la base de datos - Versión simplificada"""
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