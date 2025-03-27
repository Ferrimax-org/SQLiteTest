import sqlite3
import time
import random
from datetime import datetime
import logging
import os
import hashlib
import argparse
from maintenance import realizar_mantenimiento_power_on

class SQLiteStressTest:
    """!
    @brief Clase para realizar pruebas de estrés en SQLite
    @details Esta clase implementa métodos para probar la robustez y rendimiento
             de una base de datos SQLite, manteniendo los datos entre ejecuciones.
    """

    def __init__(self, base_path, pause_time=10, progress_interval=10):
        """!
        @brief Constructor de la clase SQLiteStressTest
        @param base_path Ruta base donde se encuentran los archivos de prueba
        @param pause_time Tiempo de pausa entre operaciones en segundos
        @param progress_interval Intervalo de actualización del progreso en segundos
        """
        self.db_path = 'stress_test.db'
        self.log_path = 'sqlite_test.log'
        self.pause_time = pause_time
        self.progress_interval = progress_interval
        
        # Crear el archivo de log vacío si no existe
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as f:
                pass
            print(f"Archivo de log creado: {self.log_path}")
            
        self.setup_logging()
        
        logging.info("-------------------")
        logging.info("Nueva sesión iniciada")
        
        # Realizar mantenimiento de power on
        if not realizar_mantenimiento_power_on():
            logging.error("Error en el mantenimiento de power on. La aplicación puede no funcionar correctamente.")
            raise Exception("Error en el mantenimiento de power on")
        
        # Inicializar la base de datos
        self.setup_database()
        if not os.path.exists(self.db_path):
            logging.info("Base de datos creada por primera vez")
        else:
            logging.info("Continuando con base de datos existente")
            
    def setup_logging(self):
        """!
        @brief Configura el sistema de logging
        """
        try:
            # Asegurarse de que el archivo de log se puede crear
            logging.basicConfig(
                filename=self.log_path,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                force=True  # Forzar la configuración del logging
            )
            print(f"Archivo de log creado en: {self.log_path}")
        except Exception as e:
            print(f"Error al configurar el logging: {e}")
            
    def setup_database(self):
        """!
        @brief Inicializa la estructura de la base de datos si no existe
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS test_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        value TEXT,
                        checksum TEXT
                    )
                ''')
                conn.commit()
                
                # Obtener el número actual de registros
                cursor.execute("SELECT COUNT(*) FROM test_data")
                count = cursor.fetchone()[0]
                logging.info(f"Registros existentes en la base de datos: {count}")
                
        except sqlite3.Error as e:
            logging.error(f"Error al acceder a la base de datos: {e}")

    def calculate_hash(self, data):
        """!
        @brief Calcula un hash MD5 consistente para los datos
        """
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def get_database_stats(self):
        """!
        @brief Obtiene estadísticas detalladas de la base de datos
        @return Diccionario con las estadísticas
        """
        stats = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener número total de registros
                cursor.execute("SELECT COUNT(*) FROM test_data")
                stats['total_records'] = cursor.fetchone()[0]
                
                # Obtener fecha del primer y último registro
                cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM test_data")
                first_date, last_date = cursor.fetchone()
                stats['first_record'] = first_date
                stats['last_record'] = last_date
                
                # Obtener tamaño de la base de datos
                stats['db_size'] = os.path.getsize(self.db_path)
                
                # Verificar integridad
                cursor.execute("SELECT value, checksum FROM test_data")
                corrupted_count = 0
                total_checked = 0
                for value, stored_checksum in cursor.fetchall():
                    total_checked += 1
                    if self.calculate_hash(value) != stored_checksum:
                        corrupted_count += 1
                stats['corrupted_records'] = corrupted_count
                stats['total_checked'] = total_checked
                stats['integrity_percentage'] = ((total_checked - corrupted_count) / total_checked * 100) if total_checked > 0 else 100
                
                # Verificar integridad de la estructura
                cursor.execute("PRAGMA integrity_check")
                integrity_check = cursor.fetchone()[0]
                stats['structural_integrity'] = integrity_check == "ok"
                
                # Obtener estadísticas de eventos del sistema
                cursor.execute("SELECT COUNT(*) FROM system_events")
                stats['total_events'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM system_events WHERE event_type = 'ERROR'")
                stats['error_events'] = cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            logging.error(f"Error al obtener estadísticas: {e}")
            stats['error'] = str(e)
            
        return stats

    def run_stress_test(self, iterations=None):
        """!
        @brief Ejecuta la prueba de estrés
        @param iterations Número de iteraciones para la prueba (None para infinito)
        """
        i = 0
        start_time = time.time()
        last_progress_time = start_time
        
        try:
            while True:  # Bucle infinito
                try:
                    # Generar datos aleatorios
                    data = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=1000))
                    timestamp = datetime.now().isoformat()
                    
                    # Calcular checksum MD5
                    checksum = self.calculate_hash(data)
                    
                    # Escribir datos
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO test_data (timestamp, value, checksum) VALUES (?, ?, ?)",
                            (timestamp, data, checksum)
                        )
                        conn.commit()
                    
                    # Mostrar progreso según el intervalo configurado
                    current_time = time.time()
                    if current_time - last_progress_time >= self.progress_interval:
                        elapsed_time = current_time - start_time
                        records_per_second = i / elapsed_time if elapsed_time > 0 else 0
                        
                        print(f"\rProgreso: {i} registros | "
                              f"Velocidad: {records_per_second:.2f} reg/s | "
                              f"Tiempo transcurrido: {elapsed_time:.1f}s | "
                              f"Tamaño DB: {os.path.getsize(self.db_path) / 1024 / 1024:.2f} MB", 
                              end='', flush=True)
                        
                        last_progress_time = current_time
                    
                    # Verificar datos cada 100 iteraciones
                    if i % 100 == 0:
                        print()  # Nueva línea para separar la verificación del progreso
                        self.verify_data()
                        logging.info(f"Iteración {i}: Verificación completada")
                    
                    i += 1
                    
                    # Esperar el tiempo especificado antes de la siguiente escritura
                    time.sleep(self.pause_time)
                        
                except sqlite3.Error as e:
                    print()  # Nueva línea para separar el error del progreso
                    logging.error(f"Error en iteración {i}: {e}")
                    
        except KeyboardInterrupt:
            print("\n")  # Nueva línea para separar el reporte final del progreso
            logging.info("Prueba interrumpida por el usuario")
            stats = self.get_database_stats()
            
            print("\n=== Reporte Final de la Base de Datos ===")
            print(f"Total de registros: {stats['total_records']}")
            print(f"Primer registro: {stats['first_record']}")
            print(f"Último registro: {stats['last_record']}")
            print(f"Tamaño de la base de datos: {stats['db_size'] / 1024 / 1024:.2f} MB")
            print("\n=== Estado de Integridad ===")
            print(f"Registros verificados: {stats['total_checked']}")
            print(f"Registros corruptos: {stats['corrupted_records']}")
            print(f"Porcentaje de integridad: {stats['integrity_percentage']:.2f}%")
            print(f"Integridad estructural: {'OK' if stats['structural_integrity'] else 'ERROR'}")
            print("\n=== Eventos del Sistema ===")
            print(f"Total de eventos: {stats['total_events']}")
            print(f"Eventos de error: {stats['error_events']}")
            print("=====================================")
            
            logging.info("=== Reporte Final ===")
            logging.info(f"Total de registros: {stats['total_records']}")
            logging.info(f"Primer registro: {stats['first_record']}")
            logging.info(f"Último registro: {stats['last_record']}")
            logging.info(f"Tamaño de la base de datos: {stats['db_size'] / 1024 / 1024:.2f} MB")
            logging.info("=== Estado de Integridad ===")
            logging.info(f"Registros verificados: {stats['total_checked']}")
            logging.info(f"Registros corruptos: {stats['corrupted_records']}")
            logging.info(f"Porcentaje de integridad: {stats['integrity_percentage']:.2f}%")
            logging.info(f"Integridad estructural: {'OK' if stats['structural_integrity'] else 'ERROR'}")
            logging.info("=== Eventos del Sistema ===")
            logging.info(f"Total de eventos: {stats['total_events']}")
            logging.info(f"Eventos de error: {stats['error_events']}")
            logging.info("===================")

    def verify_data(self):
        """!
        @brief Verifica la integridad de los datos almacenados
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value, checksum FROM test_data ORDER BY RANDOM() LIMIT 10")
            for value, stored_checksum in cursor.fetchall():
                calculated_checksum = self.calculate_hash(value)
                if calculated_checksum != stored_checksum:
                    logging.error(f"¡Error de integridad detectado! Esperado: {stored_checksum}, Calculado: {calculated_checksum}")

if __name__ == "__main__":
    """!
    @brief Punto de entrada principal del script
    """
    parser = argparse.ArgumentParser(description='Prueba de estrés para SQLite')
    parser.add_argument('--pause', type=float, default=10,
                      help='Tiempo de pausa entre operaciones en segundos (default: 10)')
    parser.add_argument('--progress-interval', type=float, default=10,
                      help='Intervalo de actualización del progreso en segundos (default: 10)')
    args = parser.parse_args()
    
    test = SQLiteStressTest('.', pause_time=args.pause, progress_interval=args.progress_interval)
    test.run_stress_test()
    