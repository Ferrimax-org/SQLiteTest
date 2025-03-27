import sqlite3
import os
import shutil
import logging
from datetime import datetime
import psutil

def verificar_integridad(db_path='stress_test.db'):
    """!
    @brief Verifica la integridad de la base de datos
    @param db_path Ruta de la base de datos
    @return bool True si la integridad es correcta
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Verificar integridad de la estructura
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            if result != "ok":
                logging.error(f"Error de integridad en la base de datos: {result}")
                return False
            return True
    except sqlite3.Error as e:
        logging.error(f"Error al verificar integridad: {e}")
        return False

def realizar_checkpoint(db_path='stress_test.db'):
    """!
    @brief Realiza un checkpoint del WAL (Write-Ahead Logging)
    @param db_path Ruta de la base de datos
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            logging.info("Checkpoint WAL realizado correctamente")
    except sqlite3.Error as e:
        logging.error(f"Error al realizar checkpoint: {e}")

def limpiar_archivos_temporales():
    """!
    @brief Limpia archivos temporales relacionados con la base de datos
    """
    temp_files = [
        'stress_test.db-shm',  # Archivo de memoria compartida
        'stress_test.db-wal',  # Archivo WAL
        'stress_test.db-journal'  # Archivo de journal
    ]
    
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                logging.info(f"Archivo temporal eliminado: {file}")
            except Exception as e:
                logging.error(f"Error al eliminar archivo temporal {file}: {e}")

def verificar_espacio(required_space_mb=100):
    """!
    @brief Verifica el espacio disponible en disco
    @param required_space_mb Espacio requerido en MB
    @return bool True si hay suficiente espacio
    """
    try:
        disk = psutil.disk_usage('/')
        free_space_mb = disk.free / (1024 * 1024)
        
        if free_space_mb < required_space_mb:
            logging.error(f"Espacio insuficiente. Disponible: {free_space_mb:.2f}MB, Requerido: {required_space_mb}MB")
            return False
            
        logging.info(f"Espacio disponible: {free_space_mb:.2f}MB")
        return True
    except Exception as e:
        logging.error(f"Error al verificar espacio: {e}")
        return False

def registrar_evento_inicio():
    """!
    @brief Registra el evento de inicio en el log
    """
    try:
        with sqlite3.connect('stress_test.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    event_type TEXT,
                    details TEXT
                )
            ''')
            
            cursor.execute(
                "INSERT INTO system_events (timestamp, event_type, details) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), 'POWER_ON', 'Inicio del sistema')
            )
            conn.commit()
            logging.info("Evento de inicio registrado correctamente")
    except sqlite3.Error as e:
        logging.error(f"Error al registrar evento de inicio: {e}")

def registrar_error(error):
    """!
    @brief Registra un error en la base de datos
    @param error Objeto de excepción
    """
    try:
        with sqlite3.connect('stress_test.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO system_events (timestamp, event_type, details) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), 'ERROR', str(error))
            )
            conn.commit()
            logging.error(f"Error registrado en la base de datos: {error}")
    except sqlite3.Error as e:
        logging.error(f"Error al registrar error en la base de datos: {e}")

def intentar_recuperacion():
    """!
    @brief Intenta recuperar el sistema de un error
    """
    try:
        # 1. Intentar realizar un checkpoint forzado
        realizar_checkpoint()
        
        # 2. Limpiar archivos temporales
        limpiar_archivos_temporales()
        
        # 3. Verificar integridad nuevamente
        if verificar_integridad():
            logging.info("Recuperación exitosa")
            return True
        else:
            logging.error("No se pudo recuperar el sistema")
            return False
    except Exception as e:
        logging.error(f"Error durante la recuperación: {e}")
        return False

def realizar_mantenimiento_power_on():
    """!
    @brief Realiza el mantenimiento del sistema al iniciar
    @return bool True si el mantenimiento fue exitoso
    """
    try:
        logging.info("Iniciando mantenimiento de power on...")
        
        # 1. Verificar integridad de la base de datos
        if not verificar_integridad():
            raise Exception("Error de integridad en la base de datos")
        
        # 2. Realizar checkpoint del WAL
        realizar_checkpoint()
        
        # 3. Limpiar archivos temporales
        limpiar_archivos_temporales()
        
        # 4. Verificar espacio en disco
        if not verificar_espacio():
            raise Exception("Espacio insuficiente en disco")
        
        # 5. Registrar evento de inicio
        registrar_evento_inicio()
        
        logging.info("Mantenimiento de power on completado exitosamente")
        return True
        
    except Exception as e:
        registrar_error(e)
        if intentar_recuperacion():
            logging.info("Sistema recuperado después del error")
            return True
        else:
            logging.error("No se pudo completar el mantenimiento de power on")
            return False 