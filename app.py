import os
import sys
import traceback
import threading
import time
from flask import Flask, session
from utils.database import Database

# ✅ CONFIGURACIÓN OBLIGATORIA PARA RAILWAY
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_RUN_PORT'] = '5000'

def create_app():
    start_time = time.time()
    
    # ✅ DEBUG INICIAL
    print("=== 🐛 INICIANDO DEBUG INTEGRADO ===")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path}")
    print(f"📋 Archivos en directorio: {os.listdir('.')}")
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # ✅ CONFIGURACIÓN AUTOMÁTICA PARA RAILWAY Y LOCAL
    print("\n=== 🔍 DETECTANDO ENTORNO ===")
    
    # Detectar si estamos en Railway
    is_railway = 'RAILWAY_ENVIRONMENT' in os.environ or 'PORT' in os.environ
    
    if is_railway:
        print("🟢 Entorno: Railway (Producción)")
        # Configuración para Railway
        app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-railway-123')
        app.config['DEBUG'] = False
        
    else:
        print("🔵 Entorno: Local (Desarrollo)")
        # Configuración para desarrollo local
        app.secret_key = 'clave-secreta-local-123'
        app.config['DEBUG'] = True
    
    print("=== ✅ CONFIGURACIÓN COMPLETADA ===\n")
    
    # ✅ VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS (NO BLOQUEANTE)
    print("🗄️ Iniciando verificación de base de datos (no bloqueante)...")
    
    def check_database():
        """Función para verificar BD en segundo plano"""
        try:
            print("   🔍 Importando Database...")
            from utils.database import Database
            db = Database()
            print("   ✅ Database importado e instanciado")
            
            # Probar conexión simple
            print("   🔌 Probando conexión a MySQL...")
            result = db.execute_query("SELECT 1", fetch_one=True)
            print(f"   🎉 Conexión a base de datos exitosa: {result}\n")
            return True
            
        except Exception as e:
            print(f"   ⚠️ Error en conexión a BD: {e}")
            print("   💡 La aplicación continuará, pero algunas funciones pueden no estar disponibles")
            print("   🔧 Verifica la configuración de MySQL en Railway\n")
            return False
    
    # Ejecutar la verificación en un hilo para no bloquear el inicio
    db_thread = threading.Thread(target=check_database, daemon=True)
    db_thread.start()
    
    # ✅ REGISTRO DE CONTROLADORES (PRIMERO, PARA INICIO RÁPIDO)
    print("🚀 Registrando controladores (inicio rápido)...")
    
    try:
        # DEBUG: Verificar carpeta controllers
        if os.path.exists('controllers'):
            print("✅ Carpeta 'controllers' encontrada")
            controller_files = os.listdir('controllers')
            print(f"📁 Archivos en controllers: {controller_files}")
        else:
            print("❌ Carpeta 'controllers' NO encontrada")
        
        # Importar controladores con manejo de errores individual
        controllers_to_import = [
            ('auth_controller', 'auth_controller'),
            ('dashboard_controller', 'dashboard_controller'),
            ('income_controller', 'income_controller'),
            ('expense_controller', 'expense_controller'),
            ('budget_controller', 'budget_controller'),
            ('savings_controller', 'savings_controller'),
            ('admin_controller', 'admin_controller')
        ]
        
        registered_controllers = 0
        
        for controller_file, controller_name in controllers_to_import:
            try:
                module = __import__(f'controllers.{controller_file}', fromlist=[controller_name])
                controller = getattr(module, controller_name)
                app.register_blueprint(controller.bp)
                print(f"✅ {controller_file} registrado")
                registered_controllers += 1
            except ImportError as e:
                print(f"❌ Error importando {controller_file}: {e}")
            except AttributeError as e:
                print(f"❌ Error en estructura de {controller_file}: {e}")
            except Exception as e:
                print(f"❌ Error inesperado en {controller_file}: {e}")
        
        print(f"📊 Controladores registrados: {registered_controllers}/{len(controllers_to_import)}\n")
        
    except Exception as e:
        print(f"❌ Error general en controladores: {e}")
        traceback.print_exc()
        print("🔧 Continuando con la aplicación...\n")
    
    # ✅ CONTEXT PROCESSORS
    @app.context_processor
    def utility_processor():
        from datetime import datetime
        return {'now': datetime.now()}
    
    @app.context_processor
    def inject_user():
        return dict(session=session)
    
    # ✅ RUTA DE PRUEBA PARA DEBUG
    @app.route('/debug')
    def debug_info():
        info = {
            'directorio_actual': os.getcwd(),
            'archivos': os.listdir('.'),
            'entorno': 'railway' if is_railway else 'local',
            'python_path': sys.path,
            'status': 'running',
            'port': os.environ.get('PORT'),
            'flask_port': os.environ.get('FLASK_RUN_PORT')
        }
        return info
    
    # ✅ RUTA DE HEALTH CHECK
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'App funcionando', 'environment': 'railway' if is_railway else 'local', 'port': os.environ.get('PORT')}
    
    # ✅ NUEVA RUTA PARA VER ESTRUCTURA DE LA TABLA
    @app.route('/ver-estructura-tabla')
    def ver_estructura_tabla():
        """Ver la estructura completa de la tabla categorias_gastos"""
        try:
            db = Database()
            
            # 1. Ver estructura de la tabla
            estructura = db.execute_query("DESCRIBE categorias_gastos", fetch=True)
            
            # 2. Ver algunos registros de ejemplo
            registros = db.execute_query("SELECT * FROM categorias_gastos LIMIT 5", fetch=True)
            
            results = [
                "<h1>📊 ESTRUCTURA DE LA TABLA categorias_gastos</h1>",
                "<h3>🔧 Estructura:</h3>",
                str(estructura),
                "<h3>📝 Registros de ejemplo:</h3>", 
                str(registros)
            ]
            
            return "<br>".join(results)
            
        except Exception as e:
            return f"Error: {e}"
    
    # ✅ RUTAS PARA ARREGLAR EMOJIS (TEMPORALES)
    @app.route('/check-charset')
    def check_charset():
        """Verificar charset actual de la BD"""
        try:
            db = Database()
            
            queries = [
                "SELECT default_character_set_name, default_collation_name FROM information_schema.SCHEMATA WHERE schema_name = 'railway'",
                "SELECT table_name, table_collation FROM information_schema.tables WHERE table_schema = 'railway' AND table_name = 'categorias_gastos'",
                "SELECT column_name, character_set_name, collation_name FROM information_schema.columns WHERE table_schema = 'railway' AND table_name = 'categorias_gastos' AND column_name IN ('nombre', 'descripcion', 'icono')"
            ]
            
            results = []
            for query in queries:
                result = db.execute_query(query, fetch=True)
                results.append(f"<h3>Query: {query}</h3>")
                results.append(str(result))
            
            return "<br>".join(results)
            
        except Exception as e:
            return f"Error: {e}"

    @app.route('/fix-db-charset')
    def fix_db_charset():
        """Ruta temporal para arreglar charset de la BD"""
        try:
            db = Database()
            
            # Comandos SQL para arreglar charset
            commands = [
                "ALTER DATABASE `railway` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
                "ALTER TABLE categorias_gastos CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
                "ALTER TABLE categorias_gastos MODIFY nombre VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
                "ALTER TABLE categorias_gastos MODIFY descripcion TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
                "ALTER TABLE categorias_gastos MODIFY icono VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            ]
            
            results = []
            for cmd in commands:
                try:
                    db.execute_query(cmd)
                    results.append(f"✅ {cmd}")
                except Exception as e:
                    results.append(f"❌ {cmd} - Error: {e}")
            
            return "<br>".join(results)
            
        except Exception as e:
            return f"Error: {e}"

    # ✅ RUTA CORREGIDA - USA EL CAMPO icono CORRECTAMENTE
    @app.route('/fix-categorias-deporte-ropa')
    def fix_categorias_deporte_ropa():
        """CREAR categorías Deporte y Ropa con emojis en el campo ICONO"""
        try:
            db = Database()
            
            results = ["<h1>🎯 CREANDO CATEGORÍAS CON EMOJIS EN ICONO</h1>"]
            
            # 1. Primero ver qué categorías existen
            try:
                all_categories = db.execute_query("SELECT id, nombre, icono, color FROM categorias_gastos ORDER BY id", fetch=True)
                results.append("<h3>🔍 CATEGORÍAS ACTUALES:</h3>")
                if all_categories:
                    for cat in all_categories:
                        results.append(f"- {cat['icono']} {cat['nombre']} (ID: {cat['id']}, Color: {cat['color']})")
                else:
                    results.append("- No hay categorías")
            except Exception as e:
                results.append(f"⚠️ Error viendo categorías: {e}")
            
            # 2. ELIMINAR categorías problemáticas
            try:
                categorias_a_eliminar = ['Deporte', 'Ropa']
                
                for nombre in categorias_a_eliminar:
                    try:
                        delete_query = "DELETE FROM categorias_gastos WHERE nombre = %s"
                        db.execute_query(delete_query, (nombre,))
                        results.append(f"✅ Eliminada: {nombre}")
                    except Exception as e:
                        results.append(f"⚠️ No se pudo eliminar {nombre}: {e}")
                        
            except Exception as e:
                results.append(f"❌ Error en eliminación: {e}")
            
            # 3. CREAR NUEVAS CATEGORÍAS CON EMOJIS EN ICONO
            try:
                # Lista de categorías a CREAR (nombre, descripcion, color, icono)
                nuevas_categorias = [
                    ('Deporte', 'Gastos en deportes y ejercicio', '#ff6b6b', '🏋️‍♂️'),
                    ('Ropa', 'Gastos en ropa y accesorios', '#4ecdc4', '👕')
                ]
                
                for nombre, descripcion, color, icono in nuevas_categorias:
                    try:
                        # Verificar si ya existe
                        check_query = "SELECT id FROM categorias_gastos WHERE nombre = %s"
                        existe = db.execute_query(check_query, (nombre,), fetch_one=True)
                        
                        if not existe:
                            # INSERTAR con todos los campos incluyendo ICONO
                            insert_query = """
                                INSERT INTO categorias_gastos (nombre, descripcion, color, icono) 
                                VALUES (%s, %s, %s, %s)
                            """
                            db.execute_query(insert_query, (nombre, descripcion, color, icono))
                            results.append(f"✅ CREADA: {icono} {nombre}")
                        else:
                            # Si existe, actualizar solo el icono
                            update_query = "UPDATE categorias_gastos SET icono = %s WHERE nombre = %s"
                            db.execute_query(update_query, (icono, nombre))
                            results.append(f"✅ ACTUALIZADA: {icono} {nombre}")
                    except Exception as e:
                        results.append(f"❌ Error con {nombre}: {e}")
                        
            except Exception as e:
                results.append(f"❌ Error en creación: {e}")
            
            # 4. Verificar que se crearon correctamente
            try:
                categorias_verificacion = db.execute_query(
                    "SELECT id, nombre, icono, color FROM categorias_gastos WHERE nombre IN ('Deporte', 'Ropa')", 
                    fetch=True
                )
                
                results.append("<h3>🎉 VERIFICACIÓN FINAL:</h3>")
                if categorias_verificacion:
                    for cat in categorias_verificacion:
                        results.append(f"✅ {cat['icono']} {cat['nombre']} - Color: {cat['color']}")
                else:
                    results.append("❌ No se encontraron las categorías creadas")
                    
            except Exception as e:
                results.append(f"❌ Error en verificación: {e}")
            
            return "<br>".join(results)
            
        except Exception as e:
            return f"Error general: {e}"
    
    # ✅ RUTA PRINCIPAL MEJORADA
    @app.route('/')
    def home():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Presupuesto Personal</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .status { padding: 20px; border-radius: 5px; margin: 10px 0; }
                .healthy { background: #d4edda; color: #155724; }
                .info { background: #d1ecf1; color: #0c5460; }
            </style>
        </head>
        <body>
            <h1>🚀 Presupuesto Personal</h1>
            <div class="status healthy">
                <h3>✅ Aplicación Funcionando</h3>
                <p>El servidor se ha iniciado correctamente.</p>
                <p><strong>Puerto:</strong> ''' + str(os.environ.get('PORT', '5000')) + '''</p>
            </div>
            <div class="status info">
                <h3>🔍 Información</h3>
                <p><strong>Entorno:</strong> ''' + ('Railway (Producción)' if is_railway else 'Local (Desarrollo)') + '''</p>
                <p><strong>Rutas disponibles:</strong></p>
                <ul>
                    <li><a href="/debug">/debug</a> - Información de diagnóstico</li>
                    <li><a href="/health">/health</a> - Estado del servicio</li>
                    <li><a href="/check-charset">/check-charset</a> - Ver charset BD</li>
                    <li><a href="/fix-db-charset">/fix-db-charset</a> - Arreglar emojis</li>
                    <li><a href="/fix-categorias-deporte-ropa">/fix-categorias-deporte-ropa</a> - Arreglar Deporte/Ropa</li>
                    <li><a href="/ver-estructura-tabla">/ver-estructura-tabla</a> - Ver estructura tabla</li>
                </ul>
            </div>
        </body>
        </html>
        '''
    
    end_time = time.time()
    print(f"🌈 Aplicación Flask inicializada correctamente en {end_time - start_time:.2f} segundos")
    return app

# ✅ INSTANCIA PRINCIPAL
try:
    app = create_app()
    print("🎉 create_app() ejecutado exitosamente")
except Exception as e:
    print(f"💥 ERROR CRÍTICO en create_app(): {e}")
    traceback.print_exc()
    # Crear app mínima como fallback
    app = Flask(__name__)
    app.secret_key = 'fallback-key'
    
    @app.route('/')
    def fallback():
        return "⚠️ Aplicación en modo fallback - Revisar logs"
    
    @app.route('/health')
    def health_fallback():
        return {'status': 'fallback', 'message': 'Modo de respaldo activado'}

# ✅ EJECUCIÓN FORZADA EN PUERTO 5000
if __name__ == '__main__':
    # FORZAR PUERTO 5000 SIEMPRE
    port = 5000
    debug_mode = False
    
    print(f"🔥 PUERTO FORZADO: {port}")
    print(f"🚀 Iniciando servidor en puerto {port}...")
    print(f"🔧 Debug mode: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)