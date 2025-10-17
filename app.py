import os
import sys
import traceback
import threading
import time
from flask import Flask, session

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
            'status': 'running'
        }
        return info
    
    # ✅ RUTA DE HEALTH CHECK
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'App funcionando', 'environment': 'railway' if is_railway else 'local'}
    
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
            </div>
            <div class="status info">
                <h3>🔍 Información</h3>
                <p><strong>Entorno:</strong> ''' + ('Railway (Producción)' if is_railway else 'Local (Desarrollo)') + '''</p>
                <p><strong>Rutas disponibles:</strong></p>
                <ul>
                    <li><a href="/debug">/debug</a> - Información de diagnóstico</li>
                    <li><a href="/health">/health</a> - Estado del servicio</li>
                </ul>
            </div>
        </body>
        </html>
        '''
    
    end_time = time.time()
    print(f"🌈 Aplicación Flask inicializada correctamente en {end_time - start_time:.2f} segundos")
    return app

# ✅ INSTANCIA PRINCIPAL (importante para gunicorn)
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

# ✅ EJECUCIÓN
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"\n🚀 Iniciando servidor en puerto {port}...")
    print(f"🔧 Debug mode: {debug_mode}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)