# Import from libraries
import time, network
from machine import ADC, Pin

# Set up the thermistor pin
thermistor_pin = ADC(26)  # Use ADC pin 26

# Set up the temperature/humidity sensor pin (DHT22)

# Set up the LUX sensor (TSL2591)

# Function to read the thermistor value
while True:
    value = thermistor_pin.read_u16()  # Read the ADC value
    voltage = value * (3.3 / 65535)  # Convert ADC value to voltage
    print("Thermistor Voltage:", voltage)  # Print the voltage
    time.sleep(1)  # Wait for 1 second before the next reading


# Function to read the temperature and humidity from the DHT22 sensor

# Function to read the LUX from the TSL2591 sensor

# Send the data
