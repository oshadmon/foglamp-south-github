# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Plugin for a INA219 Directional, High-Side, I2C Out Current/Power Monitor sensor attached using FTDI breakerboard. """

from datetime import datetime, timezone
#import math
import copy
import uuid
import logging

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions

# Code connecting to MMA8451 

# The path is specified for FogLAMP
from foglamp.plugins.south.ina219 import ina219_data_acquisition

__author__ = "Ori Shadmon"
__copyright__ = "Copyright (c) 2017 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Python module name of the plugin to load',
        'type': 'string',
        'default': 'ina219',
        'readonly': 'true'
    },
    'assetName': {
        'description': 'Asset name',
        'type': 'string',
        'default': "ina219",
        'order': "1"
    },
    'pollInterval': {
        'description': 'The interval between poll calls to the sensor poll routine expressed in milliseconds.',
        'type': 'integer',
        'default': '1000',
        'order': '2'
    },
    'gpiopin': {
        'description': 'The GPIO pin into which the DHT11 data pin is connected', 
        'type': 'integer',
        'default': '4',
        'order': '3'
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
        'name': 'mma8451',
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
    handle = copy.deepcopy(config)
    handle['sensor']=ina219_data_acquisition.INA219DataAcquisition()
    return handle


def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.

    Available for poll mode only.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        DataRetrievalError
    """
    try: 
        shunt=handle['sensor'].shunt_voltage() 
    except: 
        shunt=0 
    try:
        bus=handle['sensor'].bus_voltage()
    except:
        bus=0
    try:
        current=handle['sensor'].current_value()
    except:
        current=0
    time_stamp = utils.local_timestamp()

    """
    # For cases where you just want readings to be acceleration 
    # https://physics.stackexchange.com/questions/41653/how-do-i-get-the-total-acceleration-from-3-axes
    acceleration=math.sqrt(pow(x,2)+pow(y,2)+pow(z,2))
    rreadings = {'acceleration': acceleration} 
    """

    # unique values (x, y, z)
    readings = {'shunt voltage': shunt, 'bus voltage': bus, 'current value': current}
    wrapper = {
        'asset':     handle['assetName']['value'],
        'timestamp': time_stamp,
        'key':       str(uuid.uuid4()),
        'readings':  readings
    }
    return wrapper


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
    _LOGGER.info("Old config for INA219 plugin {} \n new config {}".format(handle, new_config))

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
    _LOGGER.info("INA219 Poll plugin shutdown")
