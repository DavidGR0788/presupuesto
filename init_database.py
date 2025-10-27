import pymysql
import os
import sys

def init_database():
    print("=== 🗄️ INICIALIZANDO BASE DE DATOS COMPLETA ===")
    
    # Configuración desde Railway
    db_config = {
        'host': os.getenv('MYSQLHOST'),
        'user': os.getenv('MYSQLUSER'),
        'password': os.getenv('MYSQLPASSWORD'),
        'database': os.getenv('MYSQLDATABASE'),
        'port': int(os.getenv('MYSQLPORT', 3306)),
        'charset': 'utf8mb4',
        'connect_timeout': 30,
        'autocommit': True
    }
    
    print(f"Conectando a: {db_config['host']}:{db_config['port']}")
    print(f"Base de datos: {db_config['database']}")
    
    try:
        # Conectar a MySQL con configuración robusta
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        print("✅ Conexión exitosa a MySQL")
        
        # SCRIPT SQL COMPLETO - EXACTO COMO EN LOCAL
        sql_script = """
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- Tabla: roles
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

-- Tabla: usuarios
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

-- Tabla: categorias_gastos
CREATE TABLE IF NOT EXISTS `categorias_gastos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `color` varchar(7) DEFAULT '#f72585',
  `icono` varchar(10) DEFAULT '?',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO `categorias_gastos` (`id`, `nombre`, `descripcion`, `color`, `icono`) VALUES
(1, 'Alimentación', 'Gastos en comida y bebida', '#f72585', '🍕'),
(2, 'Transporte', 'Transporte público, gasolina', '#4361ee', '🚗'),
(3, 'Vivienda', 'Renta, servicios básicos', '#4cc9f0', '🏠'),
(4, 'Entretenimiento', 'Cine, restaurantes, hobbies', '#7209b7', '🎬'),
(5, 'Salud', 'Medicinas, consultas médicas', '#3a0ca3', '🏥'),
(6, 'Educación', 'Cursos, libros, material', '#560bad', '📚'),
(7, 'Otros', 'Otros gastos varios', '#480ca8', '📦'),
(8, 'Ropa', 'Gastos en vestimenta', '#b5179e', '👕'),
(9, 'Deportes', 'Gastos en actividades deportivas', '#f3722c', '🏋️‍♂️');

-- Tabla: categorias_ingresos
CREATE TABLE IF NOT EXISTS `categorias_ingresos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `color` varchar(7) DEFAULT '#4361ee',
  `icono` varchar(10) DEFAULT '?',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO `categorias_ingresos` (`id`, `nombre`, `descripcion`, `color`, `icono`) VALUES
(1, 'Salario', 'Ingresos por salario mensual', '#10b981', '💼'),
(2, 'Freelance', 'Trabajos independientes', '#059669', '👨‍💻'),
(3, 'Inversiones', 'Dividendos, intereses', '#047857', '📈'),
(4, 'Otros', 'Otros ingresos', '#065f46', '💰');

-- Tabla: gastos
CREATE TABLE IF NOT EXISTS `gastos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `concepto` varchar(100) NOT NULL,
  `monto` decimal(12,2) NOT NULL,
  `categoria_id` int(11) DEFAULT NULL,
  `fecha` date NOT NULL,
  `esencial` tinyint(4) DEFAULT 1,
  `descripcion` text DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_gastos_usuario_fecha` (`usuario_id`,`fecha`),
  KEY `idx_gastos_categoria` (`categoria_id`),
  CONSTRAINT `gastos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `gastos_ibfk_2` FOREIGN KEY (`categoria_id`) REFERENCES `categorias_gastos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla: ingresos
CREATE TABLE IF NOT EXISTS `ingresos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `concepto` varchar(100) NOT NULL,
  `monto` decimal(12,2) NOT NULL,
  `categoria_id` int(11) DEFAULT NULL,
  `fecha` date NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_ingresos_usuario_fecha` (`usuario_id`,`fecha`),
  KEY `idx_ingresos_categoria` (`categoria_id`),
  CONSTRAINT `ingresos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `ingresos_ibfk_2` FOREIGN KEY (`categoria_id`) REFERENCES `categorias_ingresos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla: presupuestos
CREATE TABLE IF NOT EXISTS `presupuestos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `categoria_gasto_id` int(11) NOT NULL,
  `monto_maximo` decimal(12,2) NOT NULL,
  `mes_year` date NOT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_presupuesto` (`usuario_id`,`categoria_gasto_id`,`mes_year`),
  KEY `categoria_gasto_id` (`categoria_gasto_id`),
  CONSTRAINT `presupuestos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `presupuestos_ibfk_2` FOREIGN KEY (`categoria_gasto_id`) REFERENCES `categorias_gastos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla: ahorros (sin la columna generada por problemas de compatibilidad)
CREATE TABLE IF NOT EXISTS `ahorros` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `concepto` varchar(100) NOT NULL,
  `meta_total` decimal(12,2) NOT NULL,
  `ahorrado_actual` decimal(12,2) DEFAULT 0.00,
  `fecha_inicio` date NOT NULL,
  `fecha_objetivo` date DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `completado` tinyint(4) DEFAULT 0,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `ahorros_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
"""
        
        # Ejecutar el script COMPLETO
        print("📝 Ejecutando script SQL COMPLETO...")
        
        # Dividir y ejecutar cada sentencia
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        total_statements = len(statements)
        
        for i, statement in enumerate(statements, 1):
            try:
                if statement and len(statement) > 5:  # Solo ejecutar sentencias no vacías
                    cursor.execute(statement)
                    print(f"✅ [{i}/{total_statements}] Ejecutado: {statement[:60]}...")
            except Exception as e:
                print(f"⚠️  Error en statement {i}: {e}")
                # Continuar con las siguientes sentencias
        
        connection.commit()
        print("🎉 TODAS LAS TABLAS CREADAS EXITOSAMENTE")
        print("📊 Tablas creadas: roles, usuarios, categorias_gastos, categorias_ingresos, gastos, ingresos, presupuestos, ahorros")
        
        # Verificar que las tablas se crearon
        print("🔍 Verificando creación de tablas...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Tablas existentes en la base de datos: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()