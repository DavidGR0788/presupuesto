import os
from flask import Flask, session
from config import Config

def create_app():
    # DEBUG MEJORADO - Verificar configuración REAL
    print("=== 🚨 CONFIGURACIÓN RAILWAY ===")
    print("Variables de entorno REALES:")
    print(f"MYSQLHOST: '{os.getenv('MYSQLHOST')}'")
    print(f"MYSQLUSER: '{os.getenv('MYSQLUSER')}'")
    print(f"MYSQLPASSWORD: {'*' * len(os.getenv('MYSQLPASSWORD', ''))}")
    print(f"MYSQLDATABASE: '{os.getenv('MYSQLDATABASE')}'")
    print(f"MYSQLPORT: '{os.getenv('MYSQLPORT')}'")
    
    # Debug de la clase Config
    Config.print_debug()
    
    # Verificar si las variables están presentes
    mysql_host = os.getenv('MYSQLHOST')
    if not mysql_host:
        print("❌ ERROR CRÍTICO: MYSQLHOST no está definido")
        print("💡 Solución: Verificar que la base de datos MySQL está creada en Railway")
    else:
        print("✅ MYSQLHOST detectado correctamente")
    
    print("=== 🚨 CONFIGURACIÓN RAILWAY - FIN ===")
    
    # ✅ INICIALIZACIÓN AUTOMÁTICA DE BASE DE DATOS - FORZADA
    print("=== 🗄️ INICIALIZACIÓN FORZADA DE BASE DE DATOS ===")
    try:
        from init_database import init_database
        print("🔧 Ejecutando script de inicialización...")
        init_database()
        print("🎉 Base de datos inicializada exitosamente")
    except Exception as e:
        print(f"⚠️ Error en inicialización: {e}")
        print("🔧 Intentando verificar si las tablas ya existen...")
        try:
            from utils.database import Database
            db = Database()
            db.execute_query("SELECT 1 FROM usuarios LIMIT 1")
            print("✅ Tablas ya existen")
        except Exception as db_error:
            print(f"❌ Error crítico: Las tablas no existen y no se pueden crear: {db_error}")
            # Forzar recreación de tablas
            try:
                print("🔄 Reintentando inicialización...")
                from init_database import init_database
                init_database()
                print("🎉 Base de datos inicializada en segundo intento")
            except Exception as retry_error:
                print(f"💥 ERROR FATAL: No se pudo inicializar la base de datos: {retry_error}")
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.config.from_object(Config)
    
    # Configurar sesión para que NO sea permanente (se cierra al cerrar navegador)
    app.config['PERMANENT_SESSION_LIFETIME'] = Config.PERMANENT_SESSION_LIFETIME
    
    # Importar y registrar controladores
    from controllers.auth_controller import auth_controller
    from controllers.dashboard_controller import dashboard_controller
    from controllers.income_controller import income_controller
    from controllers.expense_controller import expense_controller
    from controllers.budget_controller import budget_controller
    from controllers.savings_controller import savings_controller
    from controllers.admin_controller import admin_controller
    
    app.register_blueprint(auth_controller.bp)
    app.register_blueprint(dashboard_controller.bp)
    app.register_blueprint(income_controller.bp)
    app.register_blueprint(expense_controller.bp)
    app.register_blueprint(budget_controller.bp)
    app.register_blueprint(savings_controller.bp)
    app.register_blueprint(admin_controller.bp)
    
    # Context processor para fechas
    @app.context_processor
    def utility_processor():
        from datetime import datetime
        return {'now': datetime.now()}
    
    return app

# Esto es importante para gunicorn - UNA SOLA INSTANCIA
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)