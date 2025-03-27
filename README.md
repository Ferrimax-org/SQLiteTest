# SQLite Stress Test

Este proyecto implementa una herramienta de prueba de estrés para bases de datos SQLite, diseñada para probar la robustez y rendimiento de la base de datos durante operaciones continuas.

## Características

- Prueba de escritura continua de datos aleatorios
- Verificación de integridad de datos mediante checksums MD5
- Logging detallado de operaciones y errores
- Reporte detallado al finalizar/interrumpir la prueba
- Tiempo de pausa configurable entre operaciones
- Persistencia de datos entre ejecuciones
- Mantenimiento automático al inicio (power on)
- Sistema de recuperación de errores

## Requisitos

- Python 3.x
- Módulos estándar de Python (sqlite3, time, random, datetime, logging, os, hashlib)
- psutil>=5.9.0

## Instalación

1. Clona o descarga este repositorio
2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Para ejecutar el programa con la configuración predeterminada (pausa de 10 segundos, actualización cada 10 segundos):

```bash
python SQLiteTest.py
```

Para especificar un tiempo de pausa personalizado (en segundos):

```bash
python SQLiteTest.py --pause 5
```

Para personalizar el intervalo de actualización del progreso:

```bash
python SQLiteTest.py --progress-interval 5
```

Para personalizar ambos parámetros:

```bash
python SQLiteTest.py --pause 5 --progress-interval 5
```

## Parámetros

- `--pause`: Tiempo de pausa entre operaciones en segundos (default: 10)
- `--progress-interval`: Intervalo de actualización del progreso en segundos (default: 10)

## Mantenimiento de Power On

Al iniciar la aplicación, se realiza automáticamente un mantenimiento que incluye:
- Verificación de integridad de la base de datos
- Checkpoint del WAL (Write-Ahead Logging)
- Limpieza de archivos temporales
- Verificación de espacio en disco
- Registro del evento de inicio

Si se detecta algún error durante el mantenimiento:
1. Se intenta una recuperación automática
2. Se registra el error en la base de datos
3. Se genera un log detallado
4. La aplicación puede detenerse si el error es crítico

## Reporte de Estado

Al interrumpir el programa con Ctrl+C, se generará un reporte detallado que incluye:
- Total de registros en la base de datos
- Fecha del primer registro
- Fecha del último registro
- Tamaño de la base de datos en MB
- Número de registros corruptos (si los hay)

## Archivos Generados

- `stress_test.db`: Base de datos SQLite con los datos de prueba
- `sqlite_test.log`: Archivo de log con información detallada de la ejecución
- Archivos temporales (se limpian automáticamente):
  - `stress_test.db-shm`: Archivo de memoria compartida
  - `stress_test.db-wal`: Archivo WAL
  - `stress_test.db-journal`: Archivo de journal

## Estructura de la Base de Datos

La base de datos contiene las siguientes tablas:
- `test_data`: Datos de prueba
  - `id`: Identificador único autoincremental
  - `timestamp`: Fecha y hora de la inserción
  - `value`: Datos aleatorios de prueba
  - `checksum`: Hash MD5 para verificación de integridad
- `system_events`: Eventos del sistema
  - `id`: Identificador único autoincremental
  - `timestamp`: Fecha y hora del evento
  - `event_type`: Tipo de evento (POWER_ON, ERROR, etc.)
  - `details`: Detalles del evento

## Verificación de Integridad

El programa realiza verificaciones de integridad:
- Cada 100 iteraciones durante la ejecución
- Al finalizar/interrumpir la prueba
- Durante el mantenimiento de power on
- Verifica que los checksums MD5 coincidan con los datos almacenados
