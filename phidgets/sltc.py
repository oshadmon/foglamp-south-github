# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Module for SLTC poll mode plugin """

import copy
import uuid
import logging

import math
from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions
from Phidget22.Devices.HumiditySensor import *
from Phidget22.Devices.TemperatureSensor import *
from Phidget22.Devices.LightSensor import *
from Phidget22.Devices.SoundSensor import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.DigitalInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *


__author__ = "Ashwin Gopalakrishnan"
__copyright__ = "Copyright (c) 2019 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"


_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'SLTC Poll Plugin',
        'type': 'string',
        'default': 'sltc',
        'readonly': 'true'
    },
    'hubSN': {
        'description': 'VINT Hub Serial Number',
        'type': 'string',
        'default': '538230',
        'order': '1',
        'displayName': 'VINT Hub SN'
    },
    'assetPrefix': {
        'description': 'Prefix of asset name',
        'type': 'string',
        'default': 'sltc/',
        'order': '2',
        'displayName': 'Asset Name Prefix'
    },
    'tempHumPort': {
        'description': 'VINT Hub port of temperature/humidity sensor',
        'type': 'string',
        'default': '2',
        'order': '3',
        'displayName': 'Humidity/Temperature Port'
    },
    'tempHumAssetName': {
        'description': 'Humidity/Temperature sensor asset name',
        'type': 'string',
        'default': 'weather',
        'order': '4',
        'displayName': 'Humidity/Temperature Asset Name'
    },
    'soundPort': {
        'description': 'VINT Hub port of sound sensor',
        'type': 'string',
        'default': '0',
        'order': '5',
        'displayName': 'Sound Port'
    },
    'soundAssetName': {
        'description': 'Sound sensor asset name',
        'type': 'string',
        'default': 'sound',
        'order': '6',
        'displayName': 'Sound Asset Name'
    },
    'lightPort': {
        'description': 'VINT Hub port of light sensor',
        'type': 'string',
        'default': '1',
        'order': '7',
        'displayName': 'Light Port'
    },
    'lightAssetName': {
        'description': 'Light sensor asset name',
        'type': 'string',
        'default': 'light',
        'order': '8',
        'displayName': 'Light Asset Name'
    },
    'motionPort': {
        'description': 'VINT Hub port of motion sensor',
        'type': 'string',
        'default': '5',
        'order': '9',
        'displayName': 'Motion Port'
    },
    'motionAssetName': {
        'description': 'Motion sensor asset name',
        'type': 'string',
        'default': 'motion',
        'order': '10',
        'displayName': 'Motion Asset Name'
    },
    'airPort': {
        'description': 'VINT Hub port of Air Quality sensor',
        'type': 'string',
        'default': '3',
        'order': '11',
        'displayName': 'Air Quality Port'
    },
    'airAssetName': {
        'description': 'Air Quality sensor asset name',
        'type': 'string',
        'default': 'air',
        'order': '12',
        'displayName': 'Air Quality Asset Name'
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
        'name': 'SLTC Poll Plugin',
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
        data['sound'] = SoundSensor()
        data['light'] = LightSensor()
        data['motion'] = DigitalInput()
        data['air'] = VoltageInput()

        data['humidity'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['humidity'].setHubPort(int(data['tempHumPort']['value']))
        data['humidity'].setIsHubPortDevice(False)
        data['humidity'].setChannel(0)

        data['temperature'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['temperature'].setHubPort(int(data['tempHumPort']['value']))
        data['temperature'].setIsHubPortDevice(False)
        data['temperature'].setChannel(0)

        data['sound'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['sound'].setHubPort(int(data['soundPort']['value']))
        data['sound'].setIsHubPortDevice(False)
        data['sound'].setChannel(0)

        data['light'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['light'].setHubPort(int(data['lightPort']['value']))
        data['light'].setIsHubPortDevice(False)
        data['light'].setChannel(0)

        data['motion'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['motion'].setHubPort(int(data['motionPort']['value']))
        data['motion'].setIsHubPortDevice(True)
        data['motion'].setChannel(0)

        data['air'].setDeviceSerialNumber(int(data['hubSN']['value']))
        data['air'].setHubPort(int(data['airPort']['value']))
        data['air'].setIsHubPortDevice(True)
        data['air'].setChannel(0)

        data['humidity'].openWaitForAttachment(5000)
        data['temperature'].openWaitForAttachment(5000)
        data['sound'].openWaitForAttachment(5000)
        data['light'].openWaitForAttachment(5000)
        data['motion'].openWaitForAttachment(5000)
        data['air'].openWaitForAttachment(5000)

        try:
            data['humidity'].getHumidity()
        except Exception as e:
            pass
        try:
            data['temperature'].getTemperature()
        except Exception as e:
            pass
        try:
            data['sound'].getdB()
        except Exception as e:
            pass
        try:
            data['light'].getIlluminance()
        except Exception as e:
            pass
        try:
            data['air'].getVoltage()
        except Exception as e:
            pass
        try:
            data['motion'].getState()
        except Exception as e:
            pass

    except Exception as ex:
        _LOGGER.exception("SLTC exception: {}".format(str(ex)))
        raise ex
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
        data.append({
            'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['tempHumAssetName']['value']),
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {
                "temperature": handle['temperature'].getTemperature(), 
                "humidity": handle['humidity'].getHumidity()
            }
        })
        data.append({
            'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['soundAssetName']['value']),
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {"loudness": handle['sound'].getdB()}
        })
        data.append({
            'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['lightAssetName']['value']),
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {"light": handle['light'].getIlluminance()}
        })
        data.append({
            'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['airAssetName']['value']),
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {"air": handle['air'].getVoltage() * air_quality_scalar}
        })
        motion = 0.0 if handle['motion'].getState() else 1.0
        data.append({
            'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['motionAssetName']['value']),
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {"motion": motion}
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

