# SQLite Stress Test

Este proyecto implementa una herramienta de prueba de estrés para bases de datos SQLite, diseñada para probar la robustez y rendimiento de la base de datos durante operaciones continuas.

## Características

- Prueba de escritura continua de datos aleatorios
- Verificación de integridad de datos mediante checksums MD5
- Logging detallado de operaciones y errores
- Reporte detallado al finalizar/interrumpir la prueba
- Tiempo de pausa configurable entre operaciones
- Persistencia de datos entre ejecuciones

## Requisitos

- Python 3.x
- Módulos estándar de Python (sqlite3, time, random, datetime, logging, os, hashlib)

## Instalación

1. Clona o descarga este repositorio
2. No se requieren dependencias adicionales

## Uso

Para ejecutar el programa con la configuración predeterminada (pausa de 10 segundos):

```bash
python SQLiteTest.py
```

Para especificar un tiempo de pausa personalizado (en segundos):

```bash
python SQLiteTest.py --pause 5
```

## Parámetros

- `--pause`: Tiempo de pausa entre operaciones en segundos (default: 10)

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

## Estructura de la Base de Datos

La base de datos contiene una tabla `test_data` con los siguientes campos:
- `id`: Identificador único autoincremental
- `timestamp`: Fecha y hora de la inserción
- `value`: Datos aleatorios de prueba
- `checksum`: Hash MD5 para verificación de integridad

## Verificación de Integridad

El programa realiza verificaciones de integridad:
- Cada 100 iteraciones durante la ejecución
- Al finalizar/interrumpir la prueba
- Verifica que los checksums MD5 coincidan con los datos almacenados
