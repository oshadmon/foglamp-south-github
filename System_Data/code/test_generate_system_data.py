"""
Name: Ori Shadmon
Date: July 2018 
Description: Testing for System_Data
"""
import aiohttp
import asyncio 
import datetime 
import json 
import os 
import queue
import requests
import time
import uuid 

import generate_system_data

class TestSystemData: 
   def setup_method(self): 
      """
      Testing of generate_system_data scripts 
      1. To run use 'pytest -s' in order to properly reset FogLAMP (each time)
      2. In order to run, make sure FogLAMP is in $HOME dir, and FogLAMP is clean/not running
      """
      self.que=queue.Queue() 

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

   def __cpu_insight(self, data:dict={}): 
      """
      Test values for cpu_insight are valid 
      :param: 
         data:dir - values to test against
      :assert: 
         Data type stored per key 
      """
      for key in data: 
         assert type(data[key]) is float

   def __mem_insight(self, data:dict={}): 
      """
      Test values for mem_insight are valid
      :param: 
         data:dir - values to test against 
      :assert: 
         1. data type of percent 
         2. warning is valid 
      """
      assert type(data['percent']) is float
      if data['warning'] == 0: 
         assert data['percent'] <= 90
      elif data['warning'] == 1: 
         assert data['percent'] > 90
      else:  
         return False 

   def __disk_insight(self, data:dict={}): 
      """
      Test values for disk_insight are valid 
      :param: 
         data:dir - dict values to test against 
      :assert: 
         1. Data type stored per key 
         2. Warning is valid
      """
      assert type(data['useage']) == float
      for key in data: 
         if key != 'useage': 
            assert type(data[key]) == int
      if data['warning'] == 0: 
         assert data['useage'] <= 75.55
      elif data['warning'] == 1: 
         assert data['useage'] > 75.55 
      else: 
         return False 

   def __battery_insight(self, data:dict={}): 
      """
      Test values for battery_percent are valid 
      """
      assert data['plugged'] == 0 or data['plugged'] == 1
      assert type(data['percent']) == float

   def test_cpu_insight(self):
      """
      retrieve data about cpu_insight, and call testing against it
      """  
      generate_system_data.cpu_insight(self.que)
      output=self.que.get()
      self.__cpu_insight(output)

   def test_mem_insight(self): 
      """
      retrieve data from mem_insight, and call data against it
      """
      generate_system_data.mem_insight(self.que)
      output=self.que.get()
      self.__mem_insight(output)

   def test_disk_insight(self): 
      """
      retrieve data from disk_insight, and call testing against it
      """
      generate_system_data.disk_insight(self.que)
      output=self.que.get()
      self.__disk_insight(output)  

   def test_battery_insight(self): 
      """
      retrieve data from battery_percent, and call testing against it
      """
      generate_system_data.battery_insight(self.que)
      output=self.que.get() 
      self.__battery_insight(output)

   def test_get_data(self): 
      """
      execute get_data, and verify data is valid 
      :assert: 
         timestamp is valid type 
      """
      timestamp, cpu_data, mem_data, disk_data, battery_data=generate_system_data.get_data() 
      assert type(timestamp) == datetime.datetime
      self.__cpu_insight(cpu_data)
      self.__mem_insight(mem_data)
      self.__disk_insight(disk_data)
      self.__battery_insight(battery_data) 

   def test_create_json(self): 
      """
      create JSON object testing 
      :assert: 
         1. Keys are valid 
         2. timestamp didn't change 
         3. uuid is valid 
      """
      timestamp, cpu_data, mem_data, disk_data, battery_data=generate_system_data.get_data()
      output=generate_system_data.create_json(timestamp, cpu_data, 'cpu') 
      assert sorted(output.keys()) == ['asset', 'key', 'readings', 'timestamp']
      assert output['asset'] == 'system_cpu'
      assert output['timestamp'] == str(timestamp)
      self.__cpu_insight(output['readings'])
      try: 
         uuid.UUID(output['key'], version=4)
      except: 
         return False

   def test_system_data_json(self):
      """
      Test that data gets sent into JSON file - generate_system_data_json.py 
      :assert: 
         1. data added to file
      """
      generate_system_data.battery_insight(self.que)
      battery_data=self.que.get() 
      generate_system_data.get_timestamp(self.que)
      timestamp=self.que.get()

      output=generate_system_data.create_json(timestamp, battery_data, 'battery')
      file_name='/tmp/%s_system_stats.json' % datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

      os.system('rm -rf %s' % file_name)
      open(file_name, 'w').close() 
      before=os.stat(file_name).st_size 
      generate_system_data.write_to_file(file_name, output) # Write to file
      after=os.stat(file_name).st_size

      assert before < after 

      os.system('rm -rf %s' % file_name)

   def test_send_to_foglamp(self): 
      """
      Test send_to_foglamp
      :assert:
         1. FogLAMP is up 
         2. Data gets sent 
         3. Validate data 
      """
      # Start FogLAMP
      foglamp=os.path.expanduser(os.path.expandvars('$HOME/FogLAMP/scripts/foglamp'))
      os.system('%s start' % foglamp)
      
      # Generate Data
      generate_system_data.battery_insight(self.que)
      battery_data=self.que.get() 
      generate_system_data.get_timestamp(self.que)
      timestamp=self.que.get()
      payload=generate_system_data.create_json(timestamp, battery_data, 'battery')
      
      time.sleep(5)
      # FogLAMP is up
      url='http://%s:%s/foglamp/asset'
      result=requests.get(url % ('localhost', 8081))
      assert result.json() == []
      
      # Send Data 
      loop=asyncio.get_event_loop()
      output=loop.run_until_complete(generate_system_data.send_to_foglamp(payload, '127.0.0.1', 6683)) 
      assert output == None
     
      time.sleep(5)
      # Validate data 
      url='http://%s:%s/foglamp/asset'
      results=requests.get(url % ('localhost', 8081)).json()
      for result in results:
         assert result['count'] == 1
         assetCode=result['assetCode']
         url='http://%s:%s/foglamp/asset/%s'
         output=requests.get(url % ('localhost', 8081, assetCode)).json()[0]
         assert str(output['timestamp']).split('.')[0] == str(timestamp).split('.')[0]
         assert output['reading']['plugged'] == battery_data['plugged']
         assert output['reading']['percent'] == battery_data['percent']

      # Stop FogLAMP 
      os.system('%s stop' % foglamp) 
      os.system('%s reset' % foglamp)
