# Tutorial on how to build a temperature, humidity, and light sensor

## Project Title

Greenhouse Summer Monitoring with Raspberry Pi Pico W and Adafruit IO

**Author**: Johanna Eriksson (je224gs)

**Project Overview**:
This project is about creating a wireless monitoring system for a greenhouse using a Raspberry Pi Pico W microcontroller. It collects temperature, humidity, and light data from the environment using a DHT22 sensor and a TSL2591 light sensor. The collected data is sent to Adafruit IO, an online cloud platform, for visualization. The aim is to gather environmental data during the growing season to optimize the automatic watering system of the greenhouse.

**Time to complete**: Approx. 6–8 hours (initial setup, coding, testing, and deployment)

## Objective

I chose to build this device to better understand the environmental conditions in my greenhouse during the summer. With insights into temperature, humidity, and light intensity, I can fine-tune the irrigation schedule of my Gardena watering system. This helps conserve water and optimize plant growth.

The system also provides a great learning opportunity for working with sensors, MicroPython, and cloud dashboards. Future upgrades will involve adding soil moisture sensors and some automation triggers, possibly even building my own irrigation system.

## Material


| Item | Purpose | Where Purchased | Cost |
| -------- | -------- | -------- | -------- |
| Raspberry Pi Pico W     | Main microcontroller     | Electrokit | ~89 SEK     |
| DHT22 sensor | Temp and humidity sensor | Electrokit | ~99 SEK |
| TSL2591 light sensor | Light intensity (lux) sensor | Electrokit | ~109 SEK |
| Breadboard & jumper wires | Circuit prototyping | Electrokit | ~50 SEK |
| USB cable | Programming and power | Already owned | – |
| Power bank (optional) | Portable deployment power source | Already owned | – |

**Sensor Specs**:

- **DHT22**: Combined temperature and humidity sensor, digital output
    * Power usage:  ~1 mA active, ~45 µA idle.
    * Humidity measuring range: 0 - 100% RH
    * Temperature measuring range: -40 till +80°C
    * Accuracy humidity (RH): ±2%
    * Accuracy temperature: ±0.5°C
- **TSL2591**: High dynamic range light sensor, I2C communication, lux value output
    * Temperature working range: -30 till +80°C
    * Light measuring range: 0.00018 - 88000 lux
    * I2C-adress: 0x29
    * Power usage: 400uA (during reading) / 5uA (while inactive)

## Computer Setup

**IDE**: Visual Studio Code (VSC)

**Steps**:

1. Flash the Raspberry Pi Pico W with MicroPython firmware from micropython.org
2. Install the PyMakr plugin in VS Code
3. Set up PyMakr to connect to the correct COM port
4. Upload files directly to the Pico using PyMakr

**Dependencies**:

- `dht.py` for DHT22
- `TSL2591.py` from [Baelcorvus' repo](https://github.com/Baelcorvus/TSL2591-Micropython-I2C-Library-for-pico)
- `umqtt.simple` for MQTT support

## Putting Everything Together

**Connections**:

- **DHT22**: Data pin to GPIO15, powered by 3.3V and GND
- **TSL2591**: SDA to GPIO0, SCL to GPIO1, powered by 3.3V and GND

**Circuit Diagram**: (Fritzing diagram to be added)

**Note**:

- Both sensors use digital interfaces (I2C, single-wire)
- No extra resistors needed for this setup
- I2C devices must not share conflicting addresses

## Platform

**Platform Used**: Adafruit IO (cloud-based)

**Why**:

- Easy MQTT integration
- Free tier is sufficient for small projects
- Clean dashboard interface

**Alternatives considered**: MIG stack (would require backend setup, so I skipped that)

Adafruit IO handles MQTT feed creation, data retention, and offers automation rules and public dashboards.

## The Code

**Core functionality**:
```python
from umqtt.simple import MQTTClient
import dht
import network
from tsl2591 import TSL2591
import time

sensor = dht.DHT22(machine.Pin(15))
tsl = TSL2591()

client = MQTTClient("client_id", "io.adafruit.com", user="AIO_USERNAME", password="AIO_KEY")
client.connect()

while True:
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    lux = tsl.lux()

    client.publish(b"AIO_USERNAME/feeds/temperature", str(temp))
    client.publish(b"AIO_USERNAME/feeds/humidity", str(hum))
    client.publish(b"AIO_USERNAME/feeds/lux", str(lux))

    time.sleep(10)
```
- Wi-Fi connected using `network.WLAN`
- MQTT via `umqtt.simple`
- TLS2591 uses external library (I2C-based)

## Transmitting the Data / Connectivity

**Transmission Details**:
- Protocol: MQTT
- Wireless: Wi-Fi (2.4GHz)
- Interval: Every 10 seconds
- MQTT payload: simple string

**Design Note**:
While Wi-Fi is convenient, range is an issue in an outdoor greenhouse. A mesh Wi-Fi repeater have been used to solve this. Alternatively, LoRa is better suited for long-range, low-power, but requires additional setup.

## Presenting the Data

**Dashboard**: Built in Adafruit IO

- Graphs and gauges for each feed
- Retains data history for days/weeks (depending on tier)
- Dashboards are customizable and sharable

**Database**: Cloud storage provided by Adafruit

**Automation**: Adafruit IO supports triggers, such as email alerts if temp exceeds threshold (not implemented yet).

## Finalizing the Design

**Final Thoughts**:
This project will hopefully achieve its goal of providing real-time greenhouse data over the summer. The setup is reliable, extensible, and beginner-friendly. Using Adafruit IO simplified the visualization process.

**Future Improvements**:

- Add battery power and deep sleep
- Add soil moisture sensor and rain sensor
- Try long-range LoRa for improved connectivity

**Photos**: (to be added later)

**Code Repository**: link to GitHub repo to be added.