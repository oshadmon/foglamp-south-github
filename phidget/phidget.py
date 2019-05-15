"""
The following is intended as the south-plugin of Dianomic's windbine demo of FogLAMP. The code uses the following Phidget based sensors: 
    - Temperature & Humidity: HUM1000_0 (https://www.phidgets.com/?tier=3&catid=14&pcid=12&prodid=644)
    - Spatial: MOT1101_0 (https://www.phidgets.com/?tier=3&catid=10&pcid=8&prodid=975)
    - Rotary: 3531_0 (https://www.phidgets.com/?tier=3&catid=103&pcid=83&prodid=404)
    - Current: VCP1100_0 (https://www.phidgets.com/?tier=3&catid=16&pcid=14&prodid=983)
"""
# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Module for Phidget poll mode plugin """

import copy
import logging
import math
import time 
import uuid 

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


__author__ = "Ashwin Gopalakrishnan"
__copyright__ = "Copyright (c) 2019 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"


_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Phidget Poll Plugin',
        'type': 'string',
        'default': 'phidget',
        'readonly': 'true'
    },
    'hubSN': {
        'description': 'VINT Hub Serial Number',
        'type': 'string',
        'default': '538854',
        'order': '1',
        'displayName': 'VINT Hub SN'
    },
    'assetPrefix': {
        'description': 'Prefix of asset name',
        'type': 'string',
        'default': 'phidget/',
        'order': '2',
        'displayName': 'Asset Name Prefix'
    },
    'tempHumAssetName': {
        'description': 'Humidity/Temperature sensor asset name',
        'type': 'string',
        'default': 'weather',
        'order': '3',
        'displayName': 'Humidity/Temperature Asset Name'
    },
    'tempHumPort': {
        'description': 'VINT Hub port of temperature/humidity sensor',
        'type': 'string',
        'default': '0',
        'order': '4',
        'displayName': 'Humidity/Temperature Port'
    },
    'tempHumPoll': {
        'description': 'Obtain Humidity/Temperature every nth time the plugin is pulled', 
        'type': 'integer', 
        'default': '1',
        'order': '5', 
        'displayName': 'Humidity/Temperature Poll', 
    }, 
    'tempHumEnable': {
        'description': 'Enable Humidity/Temperature',
        'type': 'boolean', 
        'default': 'true', 
        'order': '6', 
        'displayName': 'Enable Humidity/Temperature'
    },
    'currentAssetName': {
        'description': 'Current sensor asset name',
        'type': 'string',
        'default': 'current',
        'order': '7',
        'displayName': 'Current Asset Name'
    },
    'currentPort': {
        'description': 'VINT Hub port of current sensor',
        'type': 'string',
        'default': '3',
        'order': '8',
        'displayName': 'Current Port'
    },
    'currentPoll': {
        'description': 'Obtain current every nth time the plugin is pulled', 
        'type': 'integer', 
        'default': '1', 
        'order': '9', 
        'displayName': 'Current Poll'
    },
    'currentEnable': {
        'description': 'Enable/Disable Current sensor', 
        'type': 'boolean',
        'default': 'true', 
        'order': '10', 
        'displayName': 'Enable Current'
    },
    'encoderAssetName': {
        'description': 'Encoder sensor asset name',
        'type': 'string',
        'default': 'encoder',
        'order': '11',
        'displayName': 'Encoder Asset Name'
    },
    'encoderPort': {
        'description': 'VINT Hub port of encoder sensor',
        'type': 'string',
        'default': '1',
        'order': '12',
        'displayName': 'Encoder Port'
    },
    'encoderPoll': {
        'description': 'Obtain encoder every nth time the plugin is pulled',
        'type': 'integer',
        'default': '1',
        'order': '13',
        'displayName': 'Encoder Poll'
    },
    'encoderEnable': {
        'description': 'Enable Encoder Sensor',
        'type': 'boolean',
        'default': 'true',
        'order': '14',
        'displayName': 'Enable Encoder'
    },
    'spatialAssetName': {
        'description': 'Spatial sensors asset name',
        'type': 'string',
        'default': 'spatial',
        'order': '15',
        'displayName': 'Spatial asset name'
    },
    'spatialPort': {
        'description': 'VINT Hub port of spatial sensors', 
        'type': 'string', 
        'default': '2', 
        'order': '16', 
        'displayName': 'Spatial Port'
    },
    'accelerometerPoll': {
        'description': 'Obtain accelerometer every nth time the plugin is pulled',
        'type': 'integer',
        'default': '1',
        'order': '17',
        'displayName': 'Acceleration Poll'
    },
    'accelerometerEnable': {
        'description': 'Enable Acceleration Sensor',
        'type': 'boolean',
        'default': 'true',
        'order': '18',
        'displayName': 'Acceleration Encoder'
    },
    'gyroscopePoll': {
        'description': 'Obtain gyroscope every nth time the plugin is pulled',
        'type': 'integer',
        'default': '1',
        'order': '19',
        'displayName': 'Gyroscope Poll'
    },
    'gyroscopeEnable': {
        'description': 'Enable Gyroscope Sensor',
        'type': 'boolean',
        'default': 'true',
        'order': '20',
        'displayName': 'Enable Gyroscope'
    },
    'magnetometerPoll': {
        'description': 'Obtain magnetometer every nth time the plugin is pulled',
        'type': 'integer',
        'default': '1',
        'order': '21',
        'displayName': 'Magnetometer Poll'
    },
    'magnetometerEnable': {
        'description': 'Enable Magnetometer Sensor',
        'type': 'boolean',
        'default': 'true',
        'order': '22',
        'displayName': 'Enable Magnetometer'
    }
}

_LOGGER = logger.setup(__name__, level=logging.INFO)


def plugin_info():
    """ Returns information about the plugin.
    Args:
    Returns:
        dict: plugin information
    Raises:
    """
    return {
        'name': 'Phidget Poll Plugin',
        'version': '2.0.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
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
        data['humidity'] = HumiditySensor()
        data['temperature'] = TemperatureSensor()
        data['current'] = CurrentInput() 
        data['encoder'] = Encoder()
        data['accelerometer'] = Accelerometer()
        data['gyroscope'] = Gyroscope() 
        data['magnetometer'] = Magnetometer()
        data['last_count'] = 0

        data['humidity'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['humidity'].setHubPort(int(data['tempHumPort']['value']))
        data['humidity'].setIsHubPortDevice(False)
        data['humidity'].setChannel(0)

        data['temperature'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['temperature'].setHubPort(int(data['tempHumPort']['value']))
        data['temperature'].setIsHubPortDevice(False)
        data['temperature'].setChannel(0)

        data['current'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['current'].setHubPort(int(data['currentPort']['value']))
        data['current'].setIsHubPortDevice(False)
        data['current'].setChannel(0)

        data['encoder'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['encoder'].setHubPort(int(data['encoderPort']['value']))
        data['encoder'].setIsHubPortDevice(False)
        data['encoder'].setChannel(0)

        data['accelerometer'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['accelerometer'].setHubPort(int(data['spatialPort']['value']))
        data['accelerometer'].setIsHubPortDevice(False)
        data['accelerometer'].setChannel(0)

        data['gyroscope'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['gyroscope'].setHubPort(int(data['spatialPort']['value']))
        data['gyroscope'].setIsHubPortDevice(False)
        data['gyroscope'].setChannel(0)

        data['magnetometer'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['magnetometer'].setHubPort(int(data['spatialPort']['value']))
        data['magnetometer'].setIsHubPortDevice(False)
        data['magnetometer'].setChannel(0)

        data['humidity'].openWaitForAttachment(5000)
        data['temperature'].openWaitForAttachment(5000)
        data['current'].openWaitForAttachment(5000)
        data['encoder'].openWaitForAttachment(5000)
        data['accelerometer'].openWaitForAttachment(5000)
        data['gyroscope'].openWaitForAttachment(5000)
        data['magnetometer'].openWaitForAttachment(5000)

        try:
            data['humidity'].getHumidity()
        except Exception as e:
            pass
        try:
            data['temperature'].getTemperature()
        except Exception as e:
            pass
        try:
            data['current'].getCurrent()
        except Exception as e: 
            pass 

        i = 0 
        while i < 120:
            try:
                data['encoder'].getPosition()
            except Exception as e:
                time.sleep(1)
                i+=1 
            else: 
                break 

        i = 0
        while i < 120:
            try: 
                data['accelerometer'].getAcceleration()
            except Exception as e:
                time.sleep(1)
                i+=1
            else:
                break

        i = 0
        while i < 120:
            try:
                data['gyroscope'].getAngularRate()
            except Exception as e:
                time.sleep(1)
                i+=1
            else:
                break

        i = 0 
        while i < 120: 
            try: 
                data['magnetometer'].getMagneticField() 
            except Exception as e: 
                time.sleep(1)
                i+=1
            else: 
               break 

    except Exception as ex:
        _LOGGER.exception("Phidget exception: {}".format(str(ex)))
        raise ex

    # counter to know when to run process 
    data['tempHumCount'] = 0 
    data['currentCount'] = 0 
    data['encoderCount'] = 0 
    data['accelerometerCount'] = 0 
    data['gyroscopeCount'] = 0 
    data['magnetometerCount'] = 0 

    # counter of last encoder value 
    data['encoderPreviousValue'] = 0 

    return data


def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.
    Available for poll mode only.
    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        TimeoutError
    """
    # air quality is votlage reading between 0 and 5.1
    # we scale is to a value between 0 and 1023
    air_quality_scalar = 200.58
    try:
        time_stamp = utils.local_timestamp()
        data = list()
        if (handle['tempHumEnable']['value'] == 'true' and handle['tempHumCount'] == 0): 
            data.append({
                'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['tempHumAssetName']['value']),
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "temperature": handle['temperature'].getTemperature(),
                    "humidity": handle['humidity'].getHumidity()
                }    
            })

        if (handle['currentEnable']['value'] == 'true' and handle['currentCount'] == 0): 
            data.append({
                'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['currentAssetName']['value']),
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "current": handle['current'].getCurrent()
                }
            })

        if (handle['encoderEnable']['value'] == 'true' and handle['encoderCount'] == 0):
            value = handle['encoder'].getPosition()
            data.append({
                'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['encoderAssetName']['value']),
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "encoder": (value - handle['encoderPreviousValue'])/1200
                }
            })
            handle['encoderPreviousValue'] = value 

        if (handle['accelerometerEnable']['value'] == 'true' and handle['accelerometerCount'] == 0):
            x, y, z = handle['accelerometer'].getAcceleration()
            data.append({
                'asset': '{}{}/{}'.format(handle['assetPrefix']['value'], handle['spatialAssetName']['value'], 'accelerometer'),
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "accelerometer-x": x,
                    "accelerometer-y": y, 
                    "accelerometer-z": z
                }
            })

        if (handle['gyroscopeEnable']['value'] == 'true' and handle['gyroscopeCount'] == 0): 
            x, y, z = handle['gyroscope'].getAngularRate()
            data.append({
                'asset': '{}{}/{}'.format(handle['assetPrefix']['value'], handle['spatialAssetName']['value'], 'gyroscope'),
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "gyroscope-x": x,
                    "gyroscope-y": y,
                    "gyroscope-z": z
                }
            })

        if (handle['magnetometerEnable']['value'] == 'true' and handle['magnetometerCount'] == 0):
            x, y, z = handle['magnetometer'].getMagneticField()
            data.append({
                'asset': '{}{}/{}'.format(handle['assetPrefix']['value'], handle['spatialAssetName']['value'], 'magnetometer'),
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "magnetometer-x": x,
                    "magnetometer-y": y,
                    "magnetometer-z": z
                }  
            })

        handle['tempHumCount'] = (handle['tempHumCount'] + 1) % int(handle['tempHumPoll']['value'])
        handle['currentCount'] = (handle['currentCount'] + 1) % int(handle['currentPoll']['value']) 
        handle['encoderCount'] = (handle['encoderCount'] + 1) % int(handle['encoderPoll']['value']) 
        handle['accelerometerCount'] = (handle['accelerometerCount'] + 1) % int(handle['accelerometerPoll']['value'])
        handle['gyroscopeCount'] = (handle['gyroscopeCount'] + 1) % int(handle['gyroscopePoll']['value'])
        handle['magnetometerCount'] = (handle['magnetometerCount'] + 1) % int(handle['magnetometerPoll']['value'])

    except (Exception, RuntimeError) as ex:
        _LOGGER.exception("Phidget exception: {}".format(str(ex)))
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
    _LOGGER.info("Old config for Phidget plugin {} \n new config {}".format(handle, new_config))
    new_handle = copy.deepcopy(new_config)

    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the South plugin service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        plugin shutdown
    """
    _LOGGER.info('Phidget plugin shut down.')

