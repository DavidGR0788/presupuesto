import pymysql
import os
import sys

def init_database():
    print("=== 🗄️ INICIALIZANDO BASE DE DATOS ===")
    
    # Configuración desde Railway
    db_config = {
        'host': os.getenv('MYSQLHOST'),
        'user': os.getenv('MYSQLUSER'),
        'password': os.getenv('MYSQLPASSWORD'),
        'database': os.getenv('MYSQLDATABASE'),
        'port': int(os.getenv('MYSQLPORT', 3306)),
        'charset': 'utf8mb4'
    }
    
    print(f"Conectando a: {db_config['host']}:{db_config['port']}")
    print(f"Base de datos: {db_config['database']}")
    
    try:
        # Conectar a MySQL
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        print("✅ Conexión exitosa a MySQL")
        
        # TU SCRIPT SQL COMPLETO AQUÍ
        sql_script = """
        SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
        START TRANSACTION;
        SET time_zone = "+00:00";
        
        CREATE TABLE IF NOT EXISTS `roles` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `nombre` varchar(50) NOT NULL,
          `descripcion` varchar(255) DEFAULT NULL,
          `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
          PRIMARY KEY (`id`),
          UNIQUE KEY `nombre` (`nombre`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        
        INSERT IGNORE INTO `roles` (`id`, `nombre`, `descripcion`) VALUES
        (1, 'admin', 'Administrador del sistema'),
        (2, 'usuario', 'Usuario estándar');
        
        CREATE TABLE IF NOT EXISTS `usuarios` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `nombre` varchar(100) NOT NULL,
          `email` varchar(100) NOT NULL,
          `clave` varchar(255) NOT NULL,
          `rol_id` int(11) NOT NULL DEFAULT 2,
          `activo` tinyint(4) DEFAULT 1,
          `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
          `fecha_actualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
          PRIMARY KEY (`id`),
          UNIQUE KEY `email` (`email`),
          KEY `rol_id` (`rol_id`),
          CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        
        INSERT IGNORE INTO `usuarios` (`id`, `nombre`, `email`, `clave`, `rol_id`) VALUES
        (1, 'David Galvez', 'nelson.galvez@flyr.com', '$2b$12$dD/xz7Fx8mDPXazZqaRgoefXBSmmcBJmCFL5Dl5ijEsPXJLmzDtHW', 1);
        
        -- Continúa con el resto de tu script SQL...
        """
        
        # Ejecutar el script
        print("📝 Ejecutando script SQL...")
        for statement in sql_script.split(';'):
            if statement.strip():
                try:
                    cursor.execute(statement)
                    print(f"✅ Ejecutado: {statement[:50]}...")
                except Exception as e:
                    print(f"⚠️  En statement: {e}")
        
        connection.commit()
        print("🎉 Base de datos inicializada EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()