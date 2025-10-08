import os
from flask import Flask, session
from config import Config

def create_app():
    # DEBUG CRÍTICO - VER QUÉ ESTÁ PASANDO
    print("=== 🚨 DEBUG - INICIO ===")
    print("Variables de entorno MYSQL:")
    print(f"MYSQLHOST: '{os.getenv('MYSQLHOST')}'")
    print(f"MYSQLUSER: '{os.getenv('MYSQLUSER')}'")
    print(f"MYSQLPASSWORD: {'*' * len(os.getenv('MYSQLPASSWORD', ''))}")
    print(f"MYSQLDATABASE: '{os.getenv('MYSQLDATABASE')}'")
    print(f"MYSQLPORT: '{os.getenv('MYSQLPORT')}'")
    
    # Ver configuración cargada
    print("Configuración actual:")
    print(f"Config.MYSQL_HOST: '{Config.MYSQL_HOST}'")
    print(f"Config.MYSQL_USER: '{Config.MYSQL_USER}'")
    print(f"Config.MYSQL_DB: '{Config.MYSQL_DB}'")
    print(f"Config.MYSQL_PORT: '{Config.MYSQL_PORT}'")
    print("=== 🚨 DEBUG - FIN ===")
    
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