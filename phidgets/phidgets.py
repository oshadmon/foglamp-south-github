import copy
import uuid
import logging

import math
from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions

__author__ = "Ori Shadmon"
__copyright__ = "Copyright (c) 2019 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
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
      # for each sensor do try/catch (pass) on the first get
   except Exception as e: 
      _LOGGER.exception("SLTC exception: {}".format(str(ex)))
      raise ex 
   return data 

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
   try: 
      timestamp = utils.local_timestamp()
      data = list()
      """ Append each sensor to data list
         - asset (name) 
         - timestamp 
         - key 
         -readings {} 
      """ 
      data.append()
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

