# Import from libraries
import time, network, dht
from machine import Pin, I2C
import TSL2591

# Set up the temperature/humidity sensor pin (DHT22)
dht_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # Use GPIO 15 for DHT22
dht_sensor = dht.DHT22(dht_pin)

# Set up the LUX sensor (TSL2591)
# i2c_pin = I2C(0, scl=Pin(1), sda=Pin(0)) # Use GPIO 1 for SCL and GPIO 0 for SDA
# lux_sensor = TSL2591.TSL2591(i2c_pin)
try:
    print("Setting up I2C bus...")
    i2c_pin = I2C(1, scl=Pin(3), sda=Pin(2), freq=100000) # Use GPIO 1 for SCL and GPIO 0 for SDA, slower freq
    
    # Scan for I2C devices to debug
    print("Scanning I2C bus for any devices...")
    devices = i2c_pin.scan()
    print("Found I2C devices:", [hex(device) for device in devices])
    
    if devices:
        print(f"Great! Found {len(devices)} device(s)")
        # Check if TSL2591 is at expected address
        if 0x29 in devices:
            print("TSL2591 found at expected address 0x29")
        else:
            print("TSL2591 not at 0x29, but other devices found")
            print("Addresses found:", [hex(d) for d in devices])
    else:
        print("No I2C devices detected. Checking connections...")
        print("Expected connections:")
        print("  TSL2591 VCC -> Pico 3.3V")
        print("  TSL2591 GND -> Pico GND") 
        print("  TSL2591 SDA -> Pico GPIO 0")
        print("  TSL2591 SCL -> Pico GPIO 1")
    
    # Try to initialize the TSL2591 sensor
    if 0x29 in devices:
        lux_sensor = TSL2591.TSL2591(i2c_pin)
        print("TSL2591 sensor initialized successfully!")
    else:
        print("TSL2591 not found, running without light sensor")
        lux_sensor = None
        
except Exception as e:
    print("Error initializing TSL2591 sensor:", e)
    print("Running without light sensor...")
    lux_sensor = None

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
        if lux_sensor is None:
            return None
        ch0, ch1 = lux_sensor.raw_luminosity
        print("Raw luminosity - CH0:", ch0, "CH1:", ch1)
        lux = lux_sensor.lux
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
        client = MQTTClient(client_id=secrets['AIO_USER'], 
                            server=secrets['AIO_SERVER'], 
                            port=secrets['AIO_PORT'],
                            user=secrets['AIO_USER'], 
                            password=secrets['AIO_KEY'])
        client.connect()
        print("Connected to MQTT broker")
        return client
    except Exception as e:
        print("MQTT connection error:", e)
        return None

# Send the data
def send_data(mqtt_client, temperature, humidity, lux):
    try:
        if mqtt_client is not None:
            # Publish temperature and humidity
            mqtt_client.publish(secrets['AIO_FEED_TEMPERATURE'], str(temperature))
            mqtt_client.publish(secrets['AIO_FEED_HUMIDITY'], str(humidity))
            print(f"Published temperature: {temperature}°C, humidity: {humidity}%")
            
            # Publish LUX value
            mqtt_client.publish(secrets['AIO_FEED_LIGHT'], str(lux))
            print(f"Published LUX: {lux}")

            # Publish weather condition based on LUX value
            weather_condition = lux_to_weather_condition(lux)
            mqtt_client.publish(secrets['AIO_FEED_WEATHER'], str(weather_condition))
        else:
            print("MQTT client is not connected.")
    except Exception as e:
        print("Error sending data:", e)

# Translate LUX value to corresponding weather condition
# Need further refinement based on actual LUX values and conditions
def lux_to_weather_condition(lux):
    if lux is None:
        return "Unknown"
    elif lux < 100:
        return "Night"
    elif lux < 400:
        return "Overcast"
    elif lux < 1000:
        return "Cloudy"
    elif lux < 2000:
        return "Partly Cloudy"
    else:
        return "Sunny"

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
        weather_condition = lux_to_weather_condition(lux)

    # Send the data to the MQTT broker
        if temperature is not None and humidity is not None:
            # Only send lux data if sensor is working
            if lux is not None:
                send_data(mqtt_client, temperature, humidity, lux)
            else:
                # Send only temp/humidity if lux sensor not working
                mqtt_client.publish(secrets['AIO_FEED_TEMPERATURE'], str(temperature))
                mqtt_client.publish(secrets['AIO_FEED_HUMIDITY'], str(humidity))
                print(f"Published temperature: {temperature}°C, humidity: {humidity}% (no lux sensor)")
        else:
            print("Failed to read sensor data.")

        # Wait before the next reading
        time.sleep(10)

# Run the main function
if __name__ == '__main__':
    main()
