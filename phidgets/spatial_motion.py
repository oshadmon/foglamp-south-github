"""
Name: Ori Shadmon 
description: code for Spatial sensors (Acceleration, Gyroscope, Magnometer)
URL: https://www.phidgets.com/?tier=3&catid=10&pcid=8&prodid=975
"""

import time
from Phidget22.Devices.Spatial import *
from Phidget22.Devices.Accelerometer import * 
from Phidget22.Devices.Gyroscope import * 
from Phidget22.Devices.Magnetometer import * 
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *

ch = Accelerometer()
ch.setDeviceSerialNumber(561266) 
ch.setHubPort(4) 
ch.setIsHubPortDevice(False) 
ch.setChannel(0) 
ch.openWaitForAttachment(5000)
try: 
   ch.getAcceleration() 
except Exception as e: 
    pass 
time.sleep(5) 
print(ch.getAcceleration())
