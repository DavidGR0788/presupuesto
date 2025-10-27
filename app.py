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
    
    # ✅ RUTAS PARA ARREGLAR EMOJIS (TEMPORALES)
    @app.route('/check-charset')
    def check_charset():
        """Verificar charset actual de la BD"""
        try:
            db = Database()
            
            queries = [
                "SELECT default_character_set_name, default_collation_name FROM information_schema.SCHEMATA WHERE schema_name = 'railway'",
                "SELECT table_name, table_collation FROM information_schema.tables WHERE table_schema = 'railway' AND table_name = 'categorias_gastos'",
                "SELECT column_name, character_set_name, collation_name FROM information_schema.columns WHERE table_schema = 'railway' AND table_name = 'categorias_gastos' AND column_name IN ('nombre', 'descripcion')"
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
                "ALTER TABLE categorias_gastos MODIFY descripcion TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            ]
            
            results = []
            for cmd in commands:
                try:
                    db.execute_query(cmd)
                    results.append(f"✅ {cmd}")
                except Exception as e:
                    results.append(f"❌ {cmd} - Error: {e}")
            
            # Probar con emoji
            test_query = "INSERT INTO categorias_gastos (nombre, descripcion) VALUES (%s, %s)"
            db.execute_query(test_query, ('Test Emoji 🎉', 'Descripción con emoji ✅🚀'))
            
            return "<br>".join(results)
            
        except Exception as e:
            return f"Error: {e}"

    # ✅ RUTA CORREGIDA DEFINITIVA PARA ARREGLAR CATEGORÍAS
    @app.route('/fix-categorias-deporte-ropa')
    def fix_categorias_deporte_ropa():
        """Arreglar específicamente las categorías Deporte y Ropa con emojis correctos"""
        try:
            db = Database()
            
            results = ["<h1>🔧 Arreglando Categorías Deporte y Ropa</h1>"]
            
            # 1. Primero ver todas las categorías para diagnóstico
            try:
                all_categories = db.execute_query("SELECT id, nombre FROM categorias_gastos ORDER BY id", fetch=True)
                results.append("<h3>🔍 Todas las categorías actuales:</h3>")
                if all_categories:
                    for cat in all_categories:
                        results.append(f"- ID {cat['id']}: {cat['nombre']}")
                else:
                    results.append("- No hay categorías")
            except Exception as e:
                results.append(f"⚠️ Error viendo categorías: {e}")
            
            # 2. SOLUCIÓN SIMPLE Y DIRECTA - Eliminar por nombres exactos
            try:
                # Lista de nombres exactos a eliminar
                nombres_a_eliminar = [
                    'Deporte',
                    'Ropa', 
                    'Test Emoji 🎉',
                    'Deporte ?',
                    'Ropa ?'
                ]
                
                for nombre in nombres_a_eliminar:
                    try:
                        delete_query = f"DELETE FROM categorias_gastos WHERE nombre = '{nombre}'"
                        db.execute_query(delete_query)
                        results.append(f"✅ Eliminada: '{nombre}'")
                    except Exception as e:
                        results.append(f"⚠️ No se pudo eliminar '{nombre}': {e}")
                
            except Exception as e:
                results.append(f"❌ Error en eliminación: {e}")
            
            # 3. Crear nuevas categorías con emojis
            try:
                # Verificar si las categorías ya existen antes de crearlas
                categorias_a_crear = [
                    ('Deporte 🏋️‍♂️', 'Gastos en deportes y ejercicio'),
                    ('Ropa 👕', 'Gastos en ropa y accesorios')
                ]
                
                for nombre, descripcion in categorias_a_crear:
                    try:
                        # Verificar si ya existe
                        check_query = f"SELECT id FROM categorias_gastos WHERE nombre = '{nombre}'"
                        existe = db.execute_query(check_query, fetch_one=True)
                        
                        if not existe:
                            insert_query = f"INSERT INTO categorias_gastos (nombre, descripcion) VALUES ('{nombre}', '{descripcion}')"
                            db.execute_query(insert_query)
                            results.append(f"✅ Creada: {nombre}")
                        else:
                            results.append(f"ℹ️ Ya existe: {nombre}")
                    except Exception as e:
                        results.append(f"❌ Error creando {nombre}: {e}")
                        
            except Exception as e:
                results.append(f"❌ Error en creación: {e}")
            
            # 4. Verificar resultado final
            try:
                final_categories = db.execute_query("SELECT id, nombre FROM categorias_gastos ORDER BY id", fetch=True)
                results.append("<h3>🎉 Resultado final:</h3>")
                if final_categories:
                    for cat in final_categories:
                        emoji_status = "✅" if "🏋️‍♂️" in cat['nombre'] or "👕" in cat['nombre'] else "📝"
                        results.append(f"{emoji_status} {cat['nombre']}")
                else:
                    results.append("❌ No hay categorías")
                    
                # Verificar específicamente las categorías con emojis
                deporte_check = db.execute_query("SELECT id FROM categorias_gastos WHERE nombre = 'Deporte 🏋️‍♂️'", fetch_one=True)
                ropa_check = db.execute_query("SELECT id FROM categorias_gastos WHERE nombre = 'Ropa 👕'", fetch_one=True)
                
                results.append("<h3>🔎 Verificación específica:</h3>")
                if deporte_check:
                    results.append("✅ 'Deporte 🏋️‍♂️' está en la base de datos")
                else:
                    results.append("❌ 'Deporte 🏋️‍♂️' NO está en la base de datos")
                    
                if ropa_check:
                    results.append("✅ 'Ropa 👕' está en la base de datos")
                else:
                    results.append("❌ 'Ropa 👕' NO está en la base de datos")
                    
            except Exception as e:
                results.append(f"❌ Error en verificación final: {e}")
            
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