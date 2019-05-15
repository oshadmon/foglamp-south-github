import time
from Phidget22.Devices.Encoder import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *

# code for ch sensor
ch = Encoder()
ch.setDeviceSerialNumber(538854)
ch.setHubPort(1)
ch.setIsHubPortDevice(False)
ch.setChannel(0)
ch.openWaitForAttachment(5000)

try:
   ch.getPosition()
except Exception as e:
   pass
time.sleep(.2)
previous=0
current=0
while True:
  current=ch.getPosition()
  print(current)
  rpm = (current - previous)/1200
  print(rpm)
  previous = current

  time.sleep(1)

