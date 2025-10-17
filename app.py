import os
import sys
import traceback
from flask import Flask, session

def create_app():
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
    
    # ✅ VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS CON DEBUGGING
    print("🗄️ Verificando conexión a base de datos...")
    try:
        # DEBUG: Verificar si existe database.py
        if os.path.exists('database.py'):
            print("✅ database.py encontrado")
        else:
            print("❌ database.py NO encontrado")
            
        # Intentar importar database de diferentes formas
        try:
            from utils.database import Database
            print("✅ 'from database import Database' funcionó")
        except ImportError as e:
            print(f"❌ Error importando database: {e}")
            print("🔧 Intentando método alternativo...")
            
            # Método alternativo
            import importlib.util
            spec = importlib.util.spec_from_file_location("database", "database.py")
            database_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(database_module)
            Database = database_module.Database
            print("✅ Database importado con método alternativo")
        
        db = Database()
        print("✅ Instancia de Database creada")
        
        # Probar conexión simple
        result = db.execute_query("SELECT 1", fetch_one=True)
        print(f"🎉 Conexión a base de datos exitosa: {result}\n")
        
    except Exception as e:
        print(f"❌ Error en conexión a BD: {e}")
        print("📝 Traceback completo:")
        traceback.print_exc()
        print("\n💡 Verifica que:")
        print("   - MySQL esté ejecutándose en XAMPP")
        print("   - La base de datos 'presupuesto_personal' exista")
        print("   - El usuario 'root' tenga acceso sin contraseña")
        print("🔧 Continuando con la aplicación...\n")
    
    # ✅ REGISTRO DE CONTROLADORES CON DEBUGGING
    print("🚀 Registrando controladores...")
    
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
            'python_path': sys.path
        }
        return info
    
    # ✅ RUTA DE HEALTH CHECK
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'App funcionando'}
    
    print("🌈 Aplicación Flask inicializada correctamente con debugging")
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

# ✅ EJECUCIÓN
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"\n🚀 Iniciando servidor en puerto {port}...")
    print(f"🔧 Debug mode: {debug_mode}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)