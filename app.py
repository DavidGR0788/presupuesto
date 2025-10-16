import os
from flask import Flask, session

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # ✅ CONFIGURACIÓN AUTOMÁTICA PARA RAILWAY Y LOCAL
    print("=== 🔍 DETECTANDO ENTORNO ===")
    
    # Detectar si estamos en Railway
    is_railway = 'RAILWAY_ENVIRONMENT' in os.environ or 'PORT' in os.environ
    
    if is_railway:
        print("🟢 Entorno: Railway (Producción)")
        # Configuración para Railway
        app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-railway-123')
        app.config['DEBUG'] = False
        
        # Base de datos en Railway
        mysql_host = os.getenv('MYSQLHOST', 'localhost')
        mysql_user = os.getenv('MYSQLUSER', 'root')
        mysql_password = os.getenv('MYSQLPASSWORD', '')
        mysql_database = os.getenv('MYSQLDATABASE', 'presupuesto_personal')
        mysql_port = os.getenv('MYSQLPORT', '3306')
        
        # Construir connection string para Railway
        db_url = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}'
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        
        print(f"📦 Base de datos Railway: {mysql_host}:{mysql_port}/{mysql_database}")
        
    else:
        print("🔵 Entorno: Local (Desarrollo)")
        # Configuración para desarrollo local
        app.secret_key = 'clave-secreta-local-123'
        app.config['DEBUG'] = True
        
        # Base de datos local (XAMPP/phpMyAdmin)
        db_url = 'mysql+pymysql://root:@localhost/presupuesto_personal'
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        
        print("💻 Base de datos local: localhost/presupuesto_personal")
    
    # Configuración común para ambos entornos
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600000  # 1 hora
    
    print(f"🔗 URL de BD: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=== ✅ CONFIGURACIÓN COMPLETADA ===\n")
    
    # ✅ INICIALIZACIÓN DE BASE DE DATOS
    try:
        print("🗄️ Inicializando base de datos...")
        from init_database import init_database
        init_database()
        print("🎉 Base de datos inicializada exitosamente\n")
    except Exception as e:
        print(f"⚠️ Nota: {e}\n")
        print("🔧 Continuando - puede que las tablas ya existan\n")
    
    # ✅ REGISTRO DE CONTROLADORES
    print("🚀 Registrando controladores...")
    
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
    
    print("✅ Todos los controladores registrados\n")
    
    # ✅ CONTEXT PROCESSORS
    @app.context_processor
    def utility_processor():
        from datetime import datetime
        return {'now': datetime.now()}
    
    @app.context_processor
    def inject_user():
        return dict(session=session)
    
    print("🌈 Aplicación Flask inicializada correctamente")
    return app

# ✅ INSTANCIA PRINCIPAL (importante para gunicorn)
app = create_app()

# ✅ EJECUCIÓN
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"\n🚀 Iniciando servidor en puerto {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)