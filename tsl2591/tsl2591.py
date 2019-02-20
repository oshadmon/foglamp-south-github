# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Plugin for AM2315 temprature/humidity sensor attached using FTDI breakerboard. """

from datetime import datetime, timezone
import math
import copy
import uuid
import logging

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions

import board
import busio
import adafruit_tsl2591

__author__ = "Ori Shadmon"
__copyright__ = "Copyright (c) 2017 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Python module name of the plugin to load',
        'type': 'string',
        'default': 'tsl2591',
        'readonly': 'true'
    },
    'assetNamePrefix': {
        'description': 'Asset name',
        'type': 'string',
        'default': "tsl2591/",
        'order': "1"
    },
    'pollInterval': {
        'description': 'The interval between poll calls to the sensor poll routine expressed in milliseconds.',
        'type': 'integer',
        'default': '1000',
        'order': '2'
    },
    'luxSensorName':{
      'description': 'Asset name of Lux Sensor',
      'type': 'string',
      'default': 'lux',
      'order': '3'
   },
    'luxSensor':{
      'description': 'Enable Lux Sensor',
      'type': 'boolean',
      'default': 'true',
      'order': '4'
   },
    'infraredSensorName':{
      'description': 'Asset name of infrared Sensor',
      'type': 'string',
      'default': 'infrared',
      'order': '5'
   },
    'infraredSensor':{
      'description': 'Enable infrared Sensor',
      'type': 'boolean',
      'default': 'true',
      'order': '6'
   },
    'visibleSensorName':{
      'description': 'Asset name of visible Sensor',
      'type': 'string',
      'default': 'visible',
      'order': '7'
   },
    'visibleSensor':{
      'description': 'Enable visible Sensor',
      'type': 'boolean',
      'default': 'true',
      'order': '8'
   },
    'fullSpectrumSensorName':{
      'description': 'Asset name of fullSpectrum Sensor',
      'type': 'string',
      'default': 'fullSpectrum',
      'order': '9'
   },
    'fullSpectrumSensor':{
      'description': 'Enable fullSpectrum Sensor',
      'type': 'boolean',
      'default': 'true',
      'order': '10'
   }
}

_LOGGER = logger.setup(__name__)
""" Setup the access to the logging system of FogLAMP """
_LOGGER.setLevel(logging.INFO)


def plugin_info():
    """ Returns information about the plugin.
    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'tsl2591',
        'version': '1.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }

def plugin_init(config):
    """ Initialise the plugin.
    Args:
        config: JSON configuration document for the plugin configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """
    i2c = busio.I2C(board.SCL, board.SDA)
    handle = copy.deepcopy(config)
    handle['sensor']=adafruit_tsl2591.TSL2591(i2c)
    return handle


def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.
    Available for poll mode only.
    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor readings in a JSON document, as a Python dict, if it is available
        None - If no readings is available
    Raises:
        DataRetrievalError
    """
    time_stamp = utils.local_timestamp()
    data = list()
    asset_prefix = handle['assetNamePrefix']['value']
	
    try: 
        lux = handle['sensor'].lux
    except:
        _LOGGER.info("Unable to get lux value")
    else: 
        data.append({
           'asset': '{}{}'.format(asset_prefix, handle['luxSensorName']['value']),
           'timestamp': time_stamp, 
           'key': str(uuid.uuid4()), 
           'readings': {'lux': lux}
           }
        )
        
    try: 
        infrared = handle['sensor'].infrared
    except: 
        _LOGGER.info("Unable to get infrared value")
    else: 
        data.append({
           'asset': '{}{}'.format(asset_prefix, handle['infraredSensorName']['value']),
           'timestamp': time_stamp, 
           'key': str(uuid.uuid4()), 
           'readings': {'infrared': infrared}
           }
        )

    try: 
        visible = handle['sensor'].visible
    except:
        _LOGGER.info("Unable to get visible value")
    else: 
        data.append({
           'asset': '{}{}'.format(asset_prefix, handle['visibleSensorName']['value']),
           'timestamp': time_stamp, 
           'key': str(uuid.uuid4()), 
           'readings': {'visible': visible}
           }
        )

    try: 
        fullSpectrum = handle['sensor'].full_spectrum
    except:
        _LOGGER.info("Unable to get fullSpectrum value")
    else: 
        data.append({
           'asset': '{}{}'.format(asset_prefix, handle['fullSpectrumSensorName']['value']),
           'timestamp': time_stamp, 
           'key': str(uuid.uuid4()), 
           'readings': {'fullSpectrum': fullSpectrum}
           }
        )
        
    return data 


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin, it should be called when the configuration of the plugin is changed during the
        operation of the south service.
        The new configuration category should be passed.
    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    _LOGGER.info("Old config for AM2315 plugin {} \n new config {}".format(handle, new_config))

    new_handle = copy.deepcopy(new_config)
    new_handle['restart'] = 'no'

    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the service being shut down.
    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _LOGGER.info("AM2315 Poll plugin shutdown")
