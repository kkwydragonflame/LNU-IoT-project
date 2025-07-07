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
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print("Connecting to Wi-Fi...")
            wlan.connect(secrets['ssid'], secrets['password'])
            
            # Add timeout to prevent infinite waiting
            max_wait = 10
            while max_wait > 0:
                if wlan.isconnected():
                    break
                max_wait -= 1
                time.sleep(1)
            
            if not wlan.isconnected():
                raise Exception("Failed to connect to Wi-Fi")
                
        print("Connected to Wi-Fi:", wlan.ifconfig())
        return True
    except Exception as e:
        print("Wi-Fi connection error:", e)
        return False

# Connect to MQTT broker
def connect_mqtt():
    try:
        from umqtt.simple import MQTTClient
        client = MQTTClient(secrets['AIO_USER'], secrets['AIO_SERVER'],
                            port=secrets['AIO_PORT'],
                            user=secrets['AIO_USER'], password=secrets['AIO_KEY'])
        client.connect()
        print("Connected to MQTT broker")
        return client
    except Exception as e:
        print("MQTT connection error:", e)
        return None

# Send the data

# Main loop
def main():
    # Connect to Wi-Fi
    connect_wifi()

    # Connect to MQTT broker
    mqtt_client = connect_mqtt()

    # Read sensors
    while True:
        temperature, humidity = read_dht22()
        lux = read_lux()

    # Send the data to the MQTT broker