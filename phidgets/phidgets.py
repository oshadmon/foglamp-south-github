import copy
import uuid
import logging
import math

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions

from Phidget22.Devices.Accelerometer import *
from Phidget22.Devices.CurrentInput import *
from Phidget22.Devices.Encoder import *
from Phidget22.Devices.Gyroscope import *
from Phidget22.Devices.HumiditySensor import *
from Phidget22.Devices.Magnetometer import *
from Phidget22.Devices.TemperatureSensor import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *


__author__ = "Ori Shadmon"
__copyright__ = "Copyright (c) 2019 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
   'plugin': { 
      'description': 'Phidget Poll Plugin for Wind Turbine', 
      'type': 'string', 
      'default': 'wt_phidgets', 
      'readonly': 'true'
   },
   'assetPrefix': { 
      'description': 'Prefix asset name', 
      'type': 'string', 
      'default': 'wt_phidgets/', 
      'displayName': 'Asset Name Prefix', 
      'order': '1'
   }, 
   'hubSerialNum': {
       'descrption': 'Phidget Hub Serial Number', 
       'default': '538854', 
       'displayName': 'Phidget Hub Serial', 
       'order': '2'
   },
   'humTempAssetName': {
      'description': 'Humidity/Temperature sensor asset name', 
      'type': 'string', 
      'default': 'weather', 
      'displayName': 'Humidity/Temperature Asset Name', 
      'order': 3
   },
   'humTempPort': { 
      'description': 'Humidity/Temperature port number', 
      'type': 'string', 
      'default': '0', 
      'displayName': 'Humidity/Temperature Port'
      'order': '4', 
   },
   'currentAssetName': {
      'description': 'Current Asset Name': 
      'type': 'string', 
      'default': 'current', 
      'displayName': 'Current Asset Name', 
      'order': '5'
   }, 
   'currentPort': {
      'description': 'Current port number', 
      'type': 'string', 
      'default': '3', 
      'displayName': 'Current Port', 
      'order': '6'
   }, 
   'spatialAssetName': { 
      'description': 'Asset name for spatial sensors (accelerometer, gyroscope and magnetometer)'
      'type': 'string', 
      'default': 'spatial', 
      'displayName': 'Spatial Sensor', 
      'order': '7'
   },
   'spatialPort': {
      'description': 'Spatial port number', 
      'type': 'string', 
      'default': '2', 
      'displayName': 'Spatial Port', 
      'order':'8'
   },
   'encoderAssetName': {
      'description': 'Encoder Asset Name', 
      'type': 'string', 
      'default': 'encoder', 
      'displayName': 'Encoder Asset Name', 
      'order': '9'
   },
   'encoderPort': {
      'description': 'Encoder Port', 
      'type': 'string', 
      'default': '1', 
      'displayName': 'Encoder Port', 
      'order': '10'
   }
} 

def plugin_init(config):
   """ Initialise the plugin.
   Args:
      config: JSON configuration document for the South plugin configuration category
   Returns:
      data: JSON object to be used in future calls to the plugin
   Raises:
   """
   try: 
      data = copy.deepcopy(config) 
      """ For each sensor add: 
         - Init 
         - setDeviceSerialNumber
         - setHubPort
         - .setIsHubPortDevice
         - .setChannel
      """ 
      # humidity 
      data['humidity'] = HumiditySensor()
      data['humidity'].setDeviceSerialNumber(int(data['hubSerialNum']['value']))
      data['humidity'].setHubPort(int(data['humTempPort']['value']))
      data['humidity'].setIsHubPortDevice(False)
      data['humidity'].setChannel(0)

      # temperature 
      data['temp'] = TemperatureSensor()
      data['temp'].setDeviceSerialNumber(int(data['hubSerialNum']['value']))
      data['temp'].setHubPort(int(data['humTempPort']['value']))
      data['temp'].setIsHubPortDevice(False)
      data['temp'].setChannel(0)

      # Current 
      data['current'] = CurrentInput()
      data['current'].setDeviceSerialNumber(int(data['hubSerialNum']['value']))
      data['current'].setHubPort(int(data['currentPort']['value']))
      data['current'].setIsHubPortDevice(False)
      data['current'].setChannel(0)

      # accelerometer 
      data['accelerometer'] = Accelerometer()
      data['accelerometer'].setDeviceSerialNumber(int(data['hubSerialNum']['value']))
      data['accelerometer'].setHubPort(int(data['spatialPort']['value']))
      data['accelerometer'].setIsHubPortDevice(False)
      data['accelerometer'].setChannel(0)
      
      # gyroscope 
      data['gyroscope'] = Gyroscope()
      data['gyroscope'].setDeviceSerialNumber(int(data['hubSerialNum']['value']))
      data['gyroscope'].setHubPort(int(data['spatialPort']['value']))
      data['gyroscope'].setIsHubPortDevice(False)
      data['gyroscope'].setChannel(0)

      # magnetometer 
      data['magnetometer']= Magnetometer()
      data['magnetometer'].setDeviceSerialNumber(int(data['hubSerialNum']['value']))
      data['magnetometer'].setHubPort(int(data['spatialPort']['value']))
      data['magnetometer'].setIsHubPortDevice(False)
      data['magnetometer'].setChannel(0)

      data['encoder'] = Encoder() 
      data['encoder'].setDeviceSerialNumber(int(data['hubSerialNum']['value']))
      data['encoder'].setHubPort(int(data['encoderPort']['value']))
      data['encoder'].setIsHubPortDevice(False)
      data['encoder'].setChannel(0)

      # for each sensor do try/catch (pass) on the first get
      data['humidity'].openWaitForAttachment(5000)
      try: 
         data['humidity'].getHumidity()
      except Exception as e:
         pass 

      data['temp'].openWaitForAttachment(5000)
      try:
         data['temp'].getTemperature()
      except Exception as e:
         pass

      data['current'].openWaitForAttachment(5000)
      try: 
         data['current'].getCurrent()
      except Exception as e: 
         pass 

      data['encoder'].openWaitForAttachment(5000)
      try: 
         data['encoder'].getPosition()
      except Exception as e: 
          pass 
      i = 0
      exception = "" 
      data['accelerometer'].openWaitForAttachment(5000)
      while i < 120: 
         try:             
            data['accelerometer'].getAcceleration() 
         except Exception as e: 
            time.sleep(1)
            i+=1
            exception = e
         else: 
            break 
         if i == 120: 
            _LOGGER.exception("Failed to start accelerometer sensor... {}".format(exception))
            raise ex
      
      i = 0
      exception = ""
      data['gyroscope'].openWaitForAttachment(5000)
      while i < 120:
         try:
            data['gyroscope'].getAngularRate()
         except Exception as e:
            time.sleep(1)
            i+=1
            exception = e
         else:
            break
         if i == 120:
            _LOGGER.exception("Failed to start gyroscope sensor... {}".format(exception))
            raise ex

      i = 0
      exception = ""
      data['magnetometer'].openWaitForAttachment(5000)
      while i < 120:
         try:
            data['magnetometer'].`getMagneticField()
         except Exception as e:
            time.sleep(1)
            i+=1
            exception = e
         else:
            break
         if i == 120:
            _LOGGER.exception("Failed to start magnetometer sensor... {}".format(exception))
            raise ex


   except Exception as e: 
      _LOGGER.exception("SLTC exception: {}".format(str(ex)))
      raise ex 
   return data 

def __get_encoder_value(handle): 
   current = handle['encoder'].getPosition()
   rpm = (current - handle['encoderValue']) / 1200
   return rpm  

def plugin_pull(handle): 
   """ Extract data from sensors and return in a JSON document as a Python dict. 
       Available for poll-mode only. 
   Args: 
      handle: returns pluin initialisation call 
   Returns: 
      sensor readings ina  JSON document, as a Python dict; if available. Otherwise returns None
   Raises: 
      TimeoutError 
   """ 
   handle['encoderValue'] = 0 # init encoder value 
   try: 
      timestamp = utils.local_timestamp()
      data = list()
      """ Append each sensor to data list
         - asset (name) 
         - timestamp 
         - key 
         -readings {} 
      """ 
      data.append({
         'asset': "{}{}".format(handle['assetPrefix']['value'], handle['humTempAssetName']['value'])
         'timestamp': timestamp,
         'key': str(uuid.uuid4()), 
         'readings': { 
            "humidity": handle['humidity'].getHumidity(), 
            "temperature": handle['temp'].getTemperature()
         }
      })

      data.append({
         'asset': "{}{}".format(handle['assetPrefix']['value'], handle['currentAssetName']['value'])
         'timestamp': timestamp, 
         'key': str(uuid.uuid4()),
         'readings': { 
            "current_input": hanle['current'].getCurrent() 
         }
      }) 

      data.append({
          'asset': "{}{}".format(handle['assetPrefix']['value'], handle['spatialAssetName']['value'])
          'timestamp': timestamp, 
          'key': str(uuid.uuid4()), 
          'readings':{ 
              'accelerometer': data['accelerometer'].getAcceleration(), 
              'gyroscope': data['gyroscope'].getAngularRate(),
              'magnetometer': data['magnetometer'].getMagneticField()
          }
      })

      handle['encoderValue'] = __get_encoder_value(handle) 
      data.append({
          'asset': "{}{}".format(handle['assetPrefix']['value'], handle['encoderAssetName']['value'])
          'timestamp': timestamp,
          'key': str(uuid.uuid4()),
          'readings':{
              'encoder': handle['encoderValue'] 
          }
      })



   except (Exception, RuntimeError) as ex:
      _LOGGER.exception("SLTC exception: {}".format(str(ex)))
      raise exceptions.DataRetrievalError(ex)
   else: 
      return data 

def plugin_reconfigure(handle, new_config):
   """ Reconfigures the plugin
   Args:
       handle: handle returned by the plugin initialisation call
       new_config: JSON object representing the new configuration category for the category
   Returns:
       new_handle: new handle to be used in the future calls
   """
   _LOGGER.info("Old config for SLTC plugin {} \n new config {}".format(handle, new_config))
   new_handle = copy.deepcopy(new_config)
   return new_handle


def plugin_shutdown(handle):
   """ Shutdowns the plugin doing required cleanup, to be called prior to the South plugin service being shut down.
   Args:
       handle: handle returned by the plugin initialisation call
   Returns:
       plugin shutdown
   """
   _LOGGER.info('SLTC plugin shut down.')

