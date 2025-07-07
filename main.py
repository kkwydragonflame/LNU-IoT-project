# Import from libraries
import time, network, dht
from machine import Pin, I2C
import TSL2591

# Set up the temperature/humidity sensor pin (DHT22)
dht_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # Use GPIO 15 for DHT22
dht_sensor = dht.DHT22(dht_pin)

# Set up the LUX sensor (TSL2591)
i2c_pin = I2C(0, scl=Pin(1), sda=Pin(0)) # Use GPIO 1 for SCL and GPIO 0 for SDA
lux_sensor = TSL2591.TSL2591(i2c_pin)

# Import secrets for Wi-Fi and MQTT credentials
try:
    from secrets import secrets
except ImportError:
    print("secrets.py not found. Please create it with your Wi-Fi and MQTT credentials.")
    raise

# Function to read the temperature and humidity from the DHT22 sensor
def read_dht22():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temperature, humidity
    except Exception as e:
        print("Error reading DHT22:", e)
        return None, None

# Function to read the LUX from the TSL2591 sensor
def read_lux():
    try:
        lux = lux_sensor.lux()
        return lux
    except Exception as e:
        print("Error reading TSL2591:", e)
        return None

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(secrets['ssid'], secrets['password'])
        while not wlan.isconnected():
            time.sleep(1)
    print("Connected to Wi-Fi:", wlan.ifconfig())

# Connect to MQTT broker

# Send the data

# Main loop
def main():
    # Connect to Wi-Fi
    connect_wifi()
    
    # Connect to MQTT broker

    # Read sensors
    while True:
        temperature, humidity = read_dht22()
        lux = read_lux()

    # Send the data to the MQTT broker