"""
Name: Ori Shadmon
Description: sample code for Phidget Humidity Sensor HUM1000_0; include both Humidity & Temperature
URL: https://www.phidgets.com/?tier=3&catid=14&pcid=12&prodid=644
"""
import time
from Phidget22.Devices.HumiditySensor import *
from Phidget22.Devices.TemperatureSensor import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *

# code for humidity sensor 
humidity = HumiditySensor() 
humidity.setDeviceSerialNumber(561266)
humidity.setHubPort(5)
humidity.setIsHubPortDevice(False)
humidity.setChannel(0)
humidity.openWaitForAttachment(5000)

try:
   humidity.getHumidity()
except Exception as e: 
   pass 
time.sleep(2)
print(humidity.getHumidity())


# code for temperature sensor 
temp = TemperatureSensor() 
temp.setDeviceSerialNumber(561266)
temp.setHubPort(5)
temp.setIsHubPortDevice(False)
temp.setChannel(0)

temp.openWaitForAttachment(5000)

try:
   temp.getTemperature()
except Exception as e:
   pass
time.sleep(2)
print(temp.getTemperature())

