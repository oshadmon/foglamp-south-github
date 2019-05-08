"""
Name: Ori Shadmon 
description: code for Spatial sensors (Acceleration, Gyroscope, Magnometer)
URL: https://www.phidgets.com/?tier=3&catid=10&pcid=8&prodid=975
"""

import time
from Phidget22.Devices.CurrentInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *

ch = CurrentInput()
ch.setDeviceSerialNumber(561266) 
ch.setHubPort(3) 
ch.setIsHubPortDevice(False) 
ch.setChannel(0) 
ch.openWaitForAttachment(5000)
try: 
   ch.getCurrent() 
except Exception as e: 
    pass 
time.sleep(2) 
print(ch.getCurrent())
