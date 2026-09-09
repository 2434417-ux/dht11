import machine
import time
import gc

class DHTTimeout(Exception): pass
class DHTChecksum(Exception): pass

class DHT11:
    def __init__(self, pin_num, retries=3):
        self.pin = machine.Pin(pin_num, machine.Pin.IN, machine.Pin.PULL_UP)
        self.retries = retries

    @micropython.native
    def read(self):
        for intento in range(self.retries):
            gc.collect()
            tiempos = [0] * 40
            
            self.pin.init(machine.Pin.OUT)
            self.pin.value(0)
            time.sleep_ms(20)
            
            # SOLUCIÓN: Congelar el procesador ANTES de soltar el pin
            estado_irq = machine.disable_irq()
            try:
                self.pin.init(machine.Pin.IN, machine.Pin.PULL_UP)
                
                # Ignorar pulsos de confirmación (ACK)
                machine.time_pulse_us(self.pin, 0, 150)
                machine.time_pulse_us(self.pin, 1, 150)
                
                # Leer los 40 bits exactos
                for i in range(40):
                    t = machine.time_pulse_us(self.pin, 1, 150)
                    if t < 0: break
                    tiempos[i] = t
            finally:
                machine.enable_irq(estado_irq)

            # Si hay un 0 en el array, significa que time_pulse_us falló o se rompió el ciclo
            if 0 in tiempos:
                time.sleep(1)
                continue

            buffer = bytearray(5)
            ceros, unos = [], []
            
            for i in range(40):
                t = tiempos[i]
                if t > 40:
                    buffer[i // 8] |= (1 << (7 - (i % 8)))
                    unos.append(t)
                else:
                    ceros.append(t)
                    
            suma = (buffer[0] + buffer[1] + buffer[2] + buffer[3]) & 0xFF
            
            if suma == buffer[4] and suma != 0:
                print(f"Instrumentación -> '0': {min(ceros)}-{max(ceros)}us | '1': {min(unos)}-{max(unos)}us")
                return buffer[2], buffer[0]
            
            time.sleep(1)
            
        raise DHTChecksum("Datos corruptos tras agotar reintentos")

dht = DHT11(4)

try:
    with open("datos.csv", "w") as f:
        f.write("Temperatura,Humedad\n")
except: pass

print("Iniciando captura de 50 muestras...")
for i in range(50):
    try:
        temp, hum = dht.read()
        print(f"Muestra {i+1} -> Temp: {temp}°C, Hum: {hum}%")
        
        try:
            with open("datos.csv", "a") as f:
                f.write(f"{temp},{hum}\n")
        except: pass
        
    except Exception as e:
        print(f"Muestra {i+1} -> Fallo definitivo: {e}")
        
    time.sleep(2)
