# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Module for Phidget poll mode plugin """

import copy
import uuid
import logging

import math
from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions

from Phidget22.Devices.CurrentInput import * 
from Phidget22.Devices.Encoder import *
from Phidget22.Devices.HumiditySensor import *
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
    'tempHumPort': {
        'description': 'VINT Hub port of temperature/humidity sensor',
        'type': 'string',
        'default': '0',
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
    'currentPort': {
        'description': 'VINT Hub port of current sensor',
        'type': 'string',
        'default': '3',
        'order': '5',
        'displayName': 'Current Port'
    },
    'currentAssetName': {
        'description': 'Current sensor asset name',
        'type': 'string',
        'default': 'current',
        'order': '6',
        'displayName': 'Current Asset Name'
    },
    'encoderPort': {
        'description': 'VINT Hub port of encoder sensor',
        'type': 'string',
        'default': '1',
        'order': '7',
        'displayName': 'Encoder Port'
    },
    'encoderAssetName': {
        'description': 'Encoder sensor asset name',
        'type': 'string',
        'default': 'encoder',
        'order': '8',
        'displayName': 'Encoder Asset Name'
    },

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
        data['encoder'].setHubPort(int(data['currentPort']['value']))
        data['encoder'].setIsHubPortDevice(False)
        data['encoder'].setChannel(0)

        data['humidity'].openWaitForAttachment(5000)
        data['temperature'].openWaitForAttachment(5000)
        data['current'].openWaitForAttachment(5000)
        data['encoder'].openWaitForAttachment(5000)

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
        while i < 120 
        try:
            data['encoder'].getPosition()
        except Exception as e:
            pass

    except Exception as ex:
        _LOGGER.exception("Phidget exception: {}".format(str(ex)))
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
            'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['currentAssetName']['value']),
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {
                "current": handle['current'].getCurrent()
            }
        })
        data.append({
            'asset': '{}{}'.format(handle['assetPrefix']['value'], handle['encoderAssetName']['value']),
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {
                "current": handle['encoder'].getPosition()/1200 # number of reps
            }
        })


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

