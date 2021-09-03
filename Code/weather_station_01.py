#!/usr/bin/python3

import os
import time
from w1thermsensor import W1ThermSensor

import board
import busio
import adafruit_bme280
i2c = busio.I2C(board.SCL, board.SDA)

import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import RPi.GPIO as GPIO
import urllib
import http.client

key = os.environ.get('WRITE_KEY')


bme = adafruit_bme280.Adafruit_BME280_I2C(i2c)
ads = ADS.ADS1015(i2c)
ads.gain = 1


ds18b20 = W1ThermSensor()
 
interval = 15  #How long we want to wait between loops (seconds)
windTick = 0   #Used to count the number of times the wind speed input is triggered
rainTick = 0   #Used to count the number of times the rain input is triggered

#Set GPIO pins to use BCM pin numbers
GPIO.setmode(GPIO.BCM)

#Set digital pin 17 to an input and enable the pullup
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Set digital pin 23 to an input and enable the pullup
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Event to dectect wind (4 ticks per revolution)
GPIO.add_event_detect(17, GPIO.BOTH)
def windtrig(self):
    global windTick
    windTick += 1

GPIO.add_event_callback(17, windtrig)


#Event to dectect rainfall tick
GPIO.add_event_detect(23, GPIO.FALLING)
def raintrig(self):
    global rainTick
    rainTick += 1

GPIO.add_event_callback(23, raintrig)

 
while True:
 
    time.sleep(interval)

    #Pull temperature from DS18B20
    temperature = ds18b20.get_temperature()

    #Pull temperature from BME280
    case_temp = bme.temperature

    #Pull pressure from BME280, convert to kPA
    pressure_pa = bme.pressure
    pressure = pressure_pa / 10

    #Pull humidity from BME280
    humidity = bme.humidity

    #Calculate wind direction based on ADC reading
    chan = AnalogIn(ads, ADS.P0)
    val = chan.value
    windDir = "Not Connected"
    windDeg = 999

    if 20000 <= val <= 20500:
        windDir = "N"
        windDeg = 0
 
    if 10000 <= val <= 10500:
        windDir = "NNE"
        windDeg = 22.5
 
    if 11500 <= val <= 12000:
        windDir = "NE"
        windDeg = 45
 
    if 2000 <= val <= 2250:
        windDir = "ENE"
        windDeg = 67.5
         
    if 2300 <= val <= 2500:
        windDir = "E"
        windDeg = 90
 
    if 1500 <= val <= 1950:
        windDir = "ESE"
        windDeg = 112.5
 
    if 4500 <= val <= 4900:
        windDir = "SE"
        windDeg = 135
 
    if 3000 <= val <= 3500:
        windDir = "SSE"
        windDeg = 157.5
 
    if 7000 <= val <= 7500:
        windDir = "S"
        windDeg = 180
 
    if 6000 <= val <= 6500:
        windDir = "SSW"
        windDeg = 202.5
 
    if 16000 <= val <= 16500:
        windDir = "SW"
        windDeg = 225
 
    if 15000 <= val <= 15500:
        windDir = "WSW"
        windDeg = 247.5
 
    if 24000 <= val <= 24500:
        windDir = "W"
        windDeg = 270
 
    if 21000 <= val <= 21500:
        windDir = "WNW"
        windDeg = 292.5
 
    if 22500 <= val <= 23000:
        windDir = "NW"
        windDeg = 315
 
    if 17500 <= val <= 18500:
        windDir = "NNW"
        windDeg = 337.5

    #Calculate wind speed average over last 15 seconds
    windSpeed = (windTick * 1.2) / interval
    windTick = 0

    #Calculate accumulated rainfall over the last 15 seconds
    rainFall = rainTick * 0.2794
    rainTick = 0

    #Print the results
    #print('Temperature:    ', temperature, u'\u2103')
    #print('Humidity:       ', humidity, '%')
    #print('Pressure:       ', pressure, 'kPa')
    #print('Wind Direction: ', windDir, ' (', windDeg, ')')
    #print('Wind Speed:     ', windSpeed, 'km/h')
    #print('Rainfall:       ', rainFall, 'mm')
    #print(' ')

    params = urllib.parse.urlencode({'field1' : temperature, 'field2' : humidity, 'field3' : pressure, 'field4' : windDeg, 'field5' : windSpeed, 'field6' : rainFall, 'key' : key})

    #Configure header / connection address
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = http.client.HTTPConnection("api.thingspeak.com:80")
  
    #Try to connect to ThingSpeak and send Data
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print( response.status, response.reason)
        data = response.read()
        conn.close()
  
    #Catch the exception if the connection fails
    except:
        print("connection failed")
    
