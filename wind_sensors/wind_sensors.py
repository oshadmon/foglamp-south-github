# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Plugin for AM2315 (temperature/humidity), INA219 (Circuit), MMA8451 (Acceleration) sensors attached using FTDI breakerboard. """

import copy
import logging
import uuid

from foglamp.common import logger
from foglamp.plugins.common import utils
from pyftdi.i2c import I2cController

# Code connecting to MMA8451 
from foglamp.plugins.south.wind_sensors import am2315
from foglamp.plugins.south.wind_sensors import ina219
from foglamp.plugins.south.wind_sensors import mma8451


__author__ = "Ori Shadmon, Ashish Jabble"
__copyright__ = "Copyright (c) 2018 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Wind Sensors Poll Plugin',
        'type': 'string',
        'default': 'wind_sensors',
        'readonly': 'true'
    },
    'assetNamePrefix': {
        'description': 'Asset name prefix',
        'type': 'string',
        'default': 'wind_sensors/',
        'order': '1',
        'displayName': 'Asset Prefix Name'
    },
    'temperatureSensorName': {
        'description': 'temperature sensor name',
        'type': 'string',
        'default': "temperature",
        'order': "2",
        'displayName': 'Temperature Sensor Name'
    },
    'temperatureSensor': {
        'description': 'enable/disable the temperature sensor',
        'type': 'boolean',
        'default': 'true',
        'order': '3',
        'displayName': 'Enable Temperature Sensor'
    },
    'temperaturePollInterval': {
        'description': 'obtain temperature reading everything nth time the plugin in polled',
        'type': 'integer',
        'default': '1',
        'order': '4',
        'displayName': 'Temperature Poll Interval'
    },
    'humiditySensorName': {
        'description': 'humidity sensor name',
        'type': 'string',
        'default': 'humidity',
        'order': '5',
        'displayName': 'Humidity Sensor Name'
    },
    'humiditySensor': {
        'description':  'enable/disable the humidity sensor',
        'type': 'boolean',
        'default': 'true',
        'order': '6',
        'displayName': 'Enable Humidity Sensor'
    },
    'humidityPollInterval': {
        'description': 'obtain humidity reading everything nth time the plugin in polled',
        'type': 'integer',
        'default': '1',
        'order': '7',
        'displayName': 'Humidity Poll Interval'
    },
    'currentSensorName': {
        'description': 'current sensor name',
        'type': 'string',
        'default': 'current',
        'order': '8',
        'displayName': 'Current Sensor Name'
    },
    'currentSensor': {
        'description':  'enable/disable the current sensor',
        'type': 'boolean',
        'default': 'true',
        'order': '9',
        'displayName': 'Enable Current Sensor'
    },
    'currentPollInterval': {
        'description': 'obtain current reading everything nth time the plugin in polled',
        'type': 'integer',
        'default': '1',
        'order': '10',
        'displayName': 'Current Poll Interval'
    },
    'accelerationSensorName': {
        'description': 'acceleration sensor name',
        'type': 'string',
        'default': 'acceleration',
        'order': '11',
        'displayName': 'Acceleration Sensor Name'
    },
    'accelerationSensor': {
        'description':  'enable/disable the acceleration sensor',
        'type': 'boolean',
        'default': 'true',
        'order': '12',
        'displayName': 'Enable Acceleration Sensor'
    },
    'accelerationPollInterval': {
        'description': 'obtain acceleration reading everything nth time the plugin in polled',
        'type': 'integer',
        'default': '1',
        'order': '13',
        'displayName': 'Acceleration Poll Interval'
    },
    'i2cRetry': {
        'description': 'I2C connection retry count',
        'type': 'integer',
        'default': '1',
        'order': '14',
        'displayName': 'I2C Connection Retry Count'
    },
    'i2cURL': {
        'description': 'I2C URL address',
        'type': 'string',
        'default': 'ftdi://ftdi:232h:FT2BZHNV/1',
        'order': '15',
        'displayName': 'I2C URL Address'
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
        'name': 'Wind Sensors Poll Plugin',
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
    i2c = I2cController()
    i2c.set_retry_count(int(handle['i2cRetry']['value']))
    i2c.configure(handle['i2cURL']['value'])

    handle['am2315'] = am2315.AM2315(i2c)
    handle['ina219'] = ina219.INA219(i2c)
    handle['mma8451'] = mma8451.MMA8451(i2c)

    handle['temperatureModCount'] = 0
    handle['humidityModCount'] = 0
    handle['currentModCount'] = 0
    handle['accelerationModCount'] = 0
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
    time_stamp = utils.local_timestamp()
    wrapper = list()
    asset_prefix = handle['assetNamePrefix']['value']
    if (handle['temperatureSensor']['value'] == 'true' and
            handle['temperatureModCount'] == 0):
        asset = '{}{}'.format(asset_prefix, handle['temperatureSensorName']['value'])
        temp_wrapper = _am2315_temp(handle, asset, time_stamp)
        if temp_wrapper:
            wrapper.append(temp_wrapper)

    if (handle['humiditySensor']['value'] == 'true' and
            handle['humidityModCount'] == 0):
        asset = '{}{}'.format(asset_prefix, handle['humiditySensorName']['value'])
        humid_wrapper = _am2315_humid(handle, asset, time_stamp)
        if humid_wrapper:
            wrapper.append(humid_wrapper)

    if (handle['currentSensor']['value'] == 'true' and
            handle['currentModCount'] == 0):
        asset = '{}{}'.format(asset_prefix, handle['currentSensorName']['value'])
        current_wrapper = _ina219(handle, asset, time_stamp)
        if current_wrapper:
            wrapper.append(current_wrapper)

    if (handle['accelerationSensor']['value'] == 'true' and
            handle['accelerationModCount'] == 0):
        asset = '{}{}'.format(asset_prefix, handle['accelerationSensorName']['value'])
        a_wrapper = _mma8451(handle,  asset, time_stamp)
        if a_wrapper:
            wrapper.append(a_wrapper)

    handle['temperatureModCount'] = (handle['temperatureModCount'] + 1) % int(handle['temperaturePollInterval']['value'])
    handle['humidityModCount'] = (handle['humidityModCount'] + 1) % int(handle['humidityPollInterval']['value'])
    handle['currentModCount'] = (handle['currentModCount'] + 1) % int(handle['currentPollInterval']['value'])
    handle['accelerationModCount'] = (handle['accelerationModCount'] + 1) % int(handle['accelerationPollInterval']['value'])
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
    _LOGGER.info("Old config for Wind Sensors plugin {} \n new config {}".format(handle, new_config))

    # Find diff between old config and new config
    diff = utils.get_diff(handle, new_config)

    # Plugin should re-initialize and restart if i2cURL configuration is changed
    if 'i2cURL' in diff:
        # TODO: disconnect before restart ?
        new_handle = plugin_init(new_config)
        new_handle['restart'] = 'yes'
        _LOGGER.info("Restarting Wind Sensors plugin due to change in configuration keys [{}]".format(', '.join(diff)))
    else:
        new_handle = copy.deepcopy(new_config)
        new_handle['am2315'] = handle['am2315']
        new_handle['ina219'] = handle['ina219']
        new_handle['mma8451'] = handle['mma8451']
        new_handle['temperatureModCount'] = 0
        new_handle['humidityModCount'] = 0
        new_handle['currentModCount'] = 0
        new_handle['accelerationModCount'] = 0
        new_handle['restart'] = 'no'

    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _LOGGER.info("Wind Sensors Poll plugin shutdown")


def _am2315_temp(handle, asset, time_stamp):
    """
    Get temp data from AM2315
    :param:
       handle:config
       time_stamp: timstamp wrapper is created
    :return:
       dict object of am2315 temp data
    """
    temp_wrapper = {}
    try:
        temp = handle['am2315'].temperature()
    except:
        temp = 0.0
    if temp:
        temp_wrapper = {
            'asset': asset,
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {'temperature': temp}
        }
    return temp_wrapper


def _am2315_humid(handle, asset, time_stamp):
    """
    Get humidity data from AM2315
    :param:
       handle: config
       time_stamp: timestamp  wrapper is created
    :return:
       dict object of am2315 humdity data
    """
    humid_wrapper = {}
    try:
        humid = handle['am2315'].humidity()
    except:
        humid = 0.0
    if humid:
        humid_wrapper = {
            'asset': asset,
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {'humidity': humid}
        }
    return humid_wrapper


def _ina219(handle, asset, time_stamp):
    """
    Get data from INA219
    :param:
       handle: handle returned by the plugin initialisation call
       time_stamp: timestamp for given sensor
    :return:
       dict object of INA219 data
    """
    wrapper = {}
    try:
        current = handle['ina219'].current_value()
    except:
        current = 0.0
    if current:
        wrapper = {
            'asset': asset,
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {'current': current}
        }
    return wrapper


def _mma8451(handle, asset, time_stamp):
    """
    Get data from MMA8451
    :param:
       handle: handle returned by the plugin initialisation call
       time_stamp: timestamp for given sensor
    :return:
       dict object of mma8451 data
    """
    wrapper = {}
    try:
        x, y, z = handle['mma8451'].get_values()
    except:
        x = y = z = 0.0
    if x:
        # Based on https://physics.stackexchange.com/questions/41653/how-do-i-get-the-total-acceleration-from-3-axes
        # acceleration=math.sqrt(math.pow(x,2)+math.pow(y, 2)+math.pow(z, 2))
        wrapper = {
            'asset': asset,
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {'x': x, 'y': y, 'z': z}
        }
    return wrapper
