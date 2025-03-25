# SQLite Stress Test

## Descripción
Este módulo implementa una prueba de estrés para SQLite, diseñada específicamente para evaluar el rendimiento y la integridad de datos en sistemas con almacenamiento en tarjetas SD (como Raspberry Pi).

## Características
- Escritura continua de datos aleatorios
- Verificación periódica de integridad mediante checksums MD5
- Intervalo configurable entre escrituras (actualmente 10 segundos)
- Logging detallado de operaciones y errores
- Persistencia de datos entre sesiones
- Manejo seguro de interrupciones

## Requisitos
- Python 3.x
- SQLite3
- Módulos estándar de Python: 
  - `sqlite3`
  - `time`
  - `random`
  - `datetime`
  - `logging`
  - `os`
  - `hashlib`

## Estructura de Archivos

## Uso

### Ejecución Básica
```powershell
python SQLiteTest.py
```

### Monitoreo
Para ver los logs en tiempo real:
```powershell
Get-Content .\sqlite_test.log -Wait
```

Para verificar el tamaño de la base de datos:
```powershell
Get-Item .\stress_test.db | Select-Object Length
```

### Estructura de la Base de Datos
La tabla `test_data` contiene:
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `timestamp`: DATETIME
- `value`: TEXT (datos aleatorios)
- `checksum`: TEXT (hash MD5 para verificación)

## Funcionamiento
1. El programa crea o conecta con una base de datos SQLite
2. Genera datos aleatorios cada 10 segundos
3. Calcula un checksum MD5 para cada entrada
4. Verifica la integridad cada 100 iteraciones
5. Mantiene un log detallado de todas las operaciones
6. Continúa hasta ser interrumpido con Ctrl+C

## Logs
El archivo `sqlite_test.log` registra:
- Inicio de sesiones
- Número de registros existentes
- Verificaciones de integridad
- Errores (si ocurren)
- Estadísticas al finalizar

## Interrumpir el Programa
- Usar Ctrl+C para detener la ejecución
- El programa registrará el total de registros antes de terminar
- Los datos permanecen en la base de datos para la siguiente ejecución

## Notas de Desarrollo
- Usa MD5 para checksums consistentes entre sesiones
- Implementa manejo de excepciones para operaciones críticas
- Mantiene la integridad referencial de la base de datos
- Diseñado para pruebas de larga duración

## Posibles Mejoras Futuras
- Configuración de intervalos mediante argumentos
- Estadísticas de rendimiento detalladas
- Monitoreo del tamaño de la base de datos
- Pruebas de concurrencia
- Interfaz de línea de comandos para parámetros
