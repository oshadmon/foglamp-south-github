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

accelerometer = Accelerometer()
https://www.phidgets.com/?tier=3&catid=10&pcid=8&prodid=975




