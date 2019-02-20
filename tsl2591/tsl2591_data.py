import time 
import board
import busio
import adafruit_tsl2591

i2c = busio.I2C(board.SCL, board.SDA) 
sensor = adafruit_tsl2591.TSL2591(i2c)

def lux_sensor(): 
   return sensor.lux 

def infrared_sensor(): 
   return sensor.infrared

def visible_sensor(): 
   return sensor.visible

def spectrum_sensor():
   return sensor.full_spectrum
""
