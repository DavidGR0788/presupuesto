import pymysql
import os
from config import Config

class Database:
    def get_connection(self):
        """Obtener conexión a la base de datos"""
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
        
        # CONFIGURACIÓN SSL CORRECTA PARA RAILWAY
        if os.getenv('RAILWAY_ENV') or Config.MYSQL_HOST != 'localhost':
            # Railway requiere SSL pero sin archivo específico
            connection_config['ssl'] = {'ssl': True}
            print("🔐 Usando conexión SSL para MySQL (modo simple)")
        
        try:
            return pymysql.connect(**connection_config)
        except pymysql.err.OperationalError as e:
            print(f"❌ Error de conexión MySQL: {e}")
            print(f"🔍 Intentando conectar a: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
            raise e

    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Ejecutar consulta en la base de datos"""
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
                
                if not fetch and not fetch_one:
                    connection.commit()
                
                return result
        except Exception as e:
            connection.rollback()
            print(f"❌ Error en consulta MySQL: {e}")
            raise e
        finally:
            connection.close()