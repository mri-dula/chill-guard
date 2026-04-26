import dht
import machine
import time

from config import DATA_PIN, CHECK_INTERVAL

sensor = dht.DHT22(machine.Pin(DATA_PIN))

while True:
    try:
        sensor.measure()
        print(f"{sensor.temperature():.1f}°C")
    except OSError as e:
        print(f"ERROR: {e}")
    time.sleep(CHECK_INTERVAL)
