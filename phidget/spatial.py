"""
Name: Ori Shadmon
Description: sample code for Phidget Spatial Sensor MO1101_0; containing accelerometer, gyroscope, and magnetometer
URL: https://www.phidgets.com/?tier=3&catid=14&pcid=12&prodid=644
"""
import time
from Phidget22.Devices.Accelerometer import *
from Phidget22.Devices.Gyroscope import * 
from Phidget22.Devices.Magnetometer import * 
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *

"""
# code for accelerometer sensor 
accelerometer = Accelerometer() 
accelerometer.setDeviceSerialNumber(538854)
accelerometer.setHubPort(2)
accelerometer.setIsHubPortDevice(False)
accelerometer.setChannel(0)
accelerometer.openWaitForAttachment(5000)

i = 0 
while i < 120: 
   try:
      print(accelerometer.getAcceleration())
   except Exception as e: 
      time.sleep(1) 
      i+=1 
   else: 
       break 
   if i == 120: 
       # exit 
       pass 

print(accelerometer.getAcceleration()) 
"""
gyroscope = Gyroscope() 
gyroscope.setDeviceSerialNumber(538854)
gyroscope.setHubPort(2)
gyroscope.setIsHubPortDevice(False)
gyroscope.setChannel(0)
gyroscope.openWaitForAttachment(5000)

i = 0 
while i < 120:
   try:
      print(gyroscope.getAngularRate())
   except Exception as e:
      time.sleep(1)
      i+=1
   else:
       break
   if i == 120: 
       # exit 
       pass 
print(x, type(x)) 
print(y, type(y)) 
print(z, type(z))
"""
magnetometer = Magnetometer() 
magnetometer.setDeviceSerialNumber(538854)
magnetometer.setHubPort(2)
magnetometer.setIsHubPortDevice(False)
magnetometer.setChannel(0)
magnetometer.openWaitForAttachment(5000)

i = 0
while i < 120:
   try:
      print(magnetometer.getMagneticField())
   except Exception as e:
      time.sleep(1)
      i+=1
   else:
       break
   if i == 120:
       # exit
       pass
print(magnetometer.getMagneticField()) 
getAngularRate()"""
