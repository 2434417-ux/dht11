# Driver Custom DHT11 - MicroPython (ESP32)

## Descripción
Implementación desde cero de un controlador para el sensor DHT11 en MicroPython mediante la técnica de *bit-banging* en un solo hilo. Cumple con los requisitos de ingeniería inversa del protocolo, instrumentación de tiempos y mitigación de latencia, prescindiendo por completo de la librería estándar `dht`.

## Características Principales
* **Lectura nativa:** Decodificación de la trama de 40 bits midiendo anchos de pulso de alta precisión (`machine.time_pulse_us`).
* **Robustez y manejo de errores:** Implementación de excepciones propias (`DHTTimeout`, `DHTChecksum`) y política de reintentos acotada.
* **Mitigación de Jitter:** Optimización del intérprete usando `gc.collect()`, `machine.disable_irq()` y el decorador `@micropython.native` para proteger la zona crítica de lectura.
* **Instrumentación en tiempo real:** Reporte por consola de los tiempos mínimos y máximos (en µs) medidos para los bits '0' y '1'.
* **Almacenamiento persistente:** Registro automático de lecturas exitosas en un archivo `datos.csv` dentro del sistema de archivos del ESP32.

## Requisitos de Hardware y Software
* Placa base: ESP32 (DevKit v1 o similar)
* Firmware: MicroPython v1.20 o superior
* Sensor: DHT11 conectado al GPIO 4 (con resistencia pull-up de 10kΩ a 3.3V)

## Ejecución
Carga el script principal en el ESP32 (por ejemplo, mediante Thonny). Al ejecutar, el programa:
1. Instanciará la clase `DHT11` en el pin 4.
2. Tomará 50 muestras con un periodo de 2 segundos entre cada lectura.
3. Mostrará los datos y la instrumentación en consola.
4. Anexará automáticamente la temperatura y humedad al archivo `datos.csv`.
