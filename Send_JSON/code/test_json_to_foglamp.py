import asyncio
import json 
import os
import random
import requests
import queue
import sys
import time

import json_to_foglamp
# Code requires foglamp\_dir (under '$HOME/FogLAMP') and foglamp_south_http (under '$HOME/foglamp-south-http')
foglamp_dir=os.path.expanduser(os.path.expandvars('$HOME/foglamp-south-plugin/FogLAMP'))
sys.path.insert(0, foglamp_dir)
from foglamp import FogLAMP


class TestJSON2FogLAMP: 
   def setup_method(self): 
      """ 
      Testing of json_to_foglamp scripts
      1. To run use 'pytest -s' in order to properly reset FogLAMP (each time) 
      2. In order to run, make sure FogLAMP is in $HOME dir, and FogLAMP is clean/not running
      """  
      self.que = queue.Queue()  
      self.host='localhost' 
      self.port=6683
      self.foglamp=FogLAMP()
      self.file_name=os.path.expanduser(os.path.expandvars('$HOME/foglamp-south-plugin/System_Data/sample/2018_07_24_13_21_33_system_stats.json'))

   def __get_data(self, data:list=[], assetCode:str='')->(str, dict): 
      """
      Based on an asset, get the original cooresponding readings 
      :param: 
         data:list - list of JSON objects (created through file_to_list)
         assetCode:str - asset that the timestamp and readings correspond to
      :return: 
         timestamp and readings from data based on a given asset
      """
      for row in data: 
         output=json.loads(row)
         if output['asset'] == assetCode: 
            return output['timestamp'], output['readings']

   def test_file_to_list(self): 
      """
      Test file_to_list 
      :assert: 
         1. script returns list object with data 
         2. Assert no alteration of data occurs during transformation from file to list to JSON 
      """
      data=json_to_foglamp.file_to_list(self.file_name)
      # Assert returned object 
      assert type(data) == list
      assert len(data) > 0
      
      # Assert data is valid 
      for i in range(len(data)):
         payload=json.loads(data[i]) 
         if payload['asset'] == 'system_cpu': 
            assert payload['key'] == '28908ea6-8f7f-11e8-9a8f-0800275d93ce' 
            assert payload['timestamp'] == '2018-07-24 13:21:33.893927'
            assert payload['readings']['cpu_0'] == 100.0
            assert payload['readings']['idle'] == 9681.3
            assert payload['readings']['iowait'] == 148.55 
            assert payload['readings']['system'] == 53.64

         elif payload['asset'] == 'system_memory': 
            assert payload['key'] == '28908ea7-8f7f-11e8-9a8f-0800275d93ce'
            assert payload['timestamp'] == '2018-07-24 13:21:33.893927' 
            assert payload['readings']['warning'] == 0 
            assert payload['readings']['percent'] <= 90 

         elif payload['asset'] == 'system_battery': 
            assert payload['key'] == '28908ea9-8f7f-11e8-9a8f-0800275d93ce'
            assert payload['timestamp'] == '2018-07-24 13:21:33.893927'
            assert payload['readings']['plugged'] == 0 
            assert payload['readings']['precent'] == 82.0


   def test_send_to_foglamp(self): 
      """
      Test send_to_foglamp
      """
      loop = asyncio.get_event_loop()
      obj=json_to_foglamp.file_to_list(self.file_name)[0]
      self.foglamp.stop_foglamp()
      self.foglamp.reset_foglamp()
      self.foglamp.start_foglamp()

      loop.run_until_complete(json_to_foglamp.send_to_foglamp(obj, self.host, self.port))
      time.sleep(10) 

      url='http://localhost:8081/foglamp/asset'
      res = requests.get(url)
      result=res.json()
      print(result) 
      assert len(result) == 1

      self.foglamp.stop_foglamp()
      self.foglamp.reset_foglamp()

