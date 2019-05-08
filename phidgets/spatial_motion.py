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

spatial = Spatial() 
spatial.setDeviceSerialNumber(561266)
spatial.setHubPort(4)
spatial.setIsHubPortDevice(False)
spatial.setChannel(0)

spatial.openWaitForAttachment(5000)

# Resets the MagnetometerCorrectionParameters to their default values.
spatial.resetMagnetometerCorrectionParameters()
spatial.saveMagnetometerCorrectionParameters() 
# Re-zeros the gyroscope in 1-2 seconds. 
spatial.zeroGyro()

# Acceleration 
accelerometer = Accelerometer()
accelerometer.setDeviceSerialNumber(561266)
accelerometer.setHubPort(4)
accelerometer.setIsHubPortDevice(False)
accelerometer.setChannel(0)
accelerometer.openWaitForAttachment(5000)

try: 
   accelerometer.getAcceleration()
except Exception as e: 
   pass 
time.sleep(2) 
print(accelerometer.getAcceleration()) 

# Gyroscope
gyroscope = Gyroscope() 
gyroscope.setDeviceSerialNumber(561266)
gyroscope.setHubPort(4)
gyroscope.setIsHubPortDevice(False)
gyroscope.setChannel(0)

gyroscope.openWaitForAttachment(5000)

try: 
   gyroscope.getAngularRate()
except Exception as e: 
   pass 
time.sleep(2) 
print(gyroscope.getAngularRate()) 

# Magnetometer 
magnetometer = Magnetometer() 
magnetometer.setDeviceSerialNumber(561266)
magnetometer.setHubPort(4)
magnetometer.setIsHubPortDevice(False)
magnetometer.setChannel(0)
magnetometer.openWaitForAttachment(5000)

try: 
    magnetometer.getMagneticField()
except Exception as e: 
    pass 
time.sleep(2) 
print(magnetometer.getMagneticField())


