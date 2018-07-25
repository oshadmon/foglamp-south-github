import asyncio
import json 
import os
import random
import requests
import queue
import time
import urllib.request

import json_to_foglamp

class TestJSON2FogLAMP: 
   def setup_method(self): 
      """ 
      Testing of json_to_foglamp scripts
      1. To run use 'pytest -s' in order to properly reset FogLAMP (each time) 
      2. In order to run, make sure FogLAMP is in $HOME dir, and FogLAMP is clean/not running
      """  
      self.que = queue.Queue()  
      self.foglamp=os.path.expanduser(os.path.expandvars('$HOME/FogLAMP/scripts/foglamp'))
      self.file_name=os.path.expanduser(os.path.expandvars('$HOME/foglamp-south-plugin/System_Data/sample/2018_07_24_13_21_33_system_stats.json'))
      self.__start_foglamp()
      time.sleep(5)

   def teardown_method(self): 
      self.__stop_foglamp() 
      self.__reset_foglamp()

   def __stop_foglamp(self):
      """
      Stop FogLAMP
       """
      os.system('%s stop' % self.foglamp) 
   def __reset_foglamp(self): 
      """
      Reset FogLAMP
      """ 
      os.system('%s reset' % self.foglamp)
   def __start_foglamp(self): 
      """
      Start FogLAMP
      """
      os.system('%s start' % self.foglamp)

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
     
      for i in range(len(data)):
         payload=json.loads(data[i]) 
         # Assert Actual data
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
      :assert:
         1. FogLAMP is up 
         2. Data gets sent 
         3. Something was retrieve (on FogLAMP side)
         4. Values are correct 
      """
      # Generate data 
      data=json_to_foglamp.file_to_list(self.file_name)
      
      # FogLAMP is up
      url='http://%s:%s/foglamp/asset'
      result=requests.get(url % ('localhost', 8081))
      assert result.json() == []

      # Send data 
      loop=asyncio.get_event_loop() 
      for i in range(len(data)): 
         payload=data[i]
         output=loop.run_until_complete(json_to_foglamp.send_to_foglamp(payload, '127.0.0.1', 6683)) 
         assert output == 0

      time.sleep(5)
      url='http://%s:%s/foglamp/asset'
      results=requests.get(url % ('localhost', 8081)).json() 
      for result in results: 
         assert result['count'] == 1
         assetCode=result['assetCode']
         url='http://%s:%s/foglamp/asset/%s' 
         output=requests.get(url % ('localhost', 8081, assetCode)).json()[0]
         timestamp, readings=self.__get_data(data, assetCode)
         '''
         {'timestamp': '2018-07-24 13:21:33.893', 'reading': {'precent': 82.0, 'plugged': 0}}
         {'timestamp': '2018-07-24 13:21:33.893', 'reading': {'iowait': 148.55, 'system': 53.64, 'cpu_0': 100.0, 'idle': 9681.3}}
         {'timestamp': '2018-07-24 13:21:33.893', 'reading': {'read': 18618, 'useage': 30.0, 'warning': 0, 'write': 599646}}
         {'timestamp': '2018-07-24 13:21:33.893', 'reading': {'percent': 35.2, 'warning': 0}}
         '''
         assert output['timestamp'].split(".")[0] == timestamp.split(".")[0]
         for key in sorted(readings.keys()): 
            assert output['reading'][key] == readings[key]
            

"""
system_battery {'timestamp': '2018-07-24 13:21:33.893', 'reading': {'plugged': 0, 'precent': 82.0}}
system_cpu {'timestamp': '2018-07-24 13:21:33.893', 'reading': {'cpu_0': 100.0, 'iowait': 148.55, 'idle': 9681.3, 'system': 53.64}}
system_disk {'timestamp': '2018-07-24 13:21:33.893', 'reading': {'write': 599646, 'useage': 30.0, 'read': 18618, 'warning': 0}}
system_memory {'timestamp': '2018-07-24 13:21:33.893', 'reading': {'warning': 0, 'percent': 35.2}}
""" 
