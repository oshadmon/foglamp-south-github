"""
Name: Ori Shadmon
Date: July 2018 
Description: Testing for System_Data 
"""
import datetime 
import json 
import os 
import queue
import uuid 

from generate_system_data import get_timestamp, cpu_insight, mem_insight, disk_insight, get_data, create_json, main

class TestSystemData: 
   def setup_method(self): 
      os.system('rm -rf /tmp/*.json')
      self.que=queue.Queue()

   def teardown_method(self): 
      os.system('rm -rf /tmp/*.json')

   def test_get_timestamp(self): 
      """
      Test get_timestamp
      :assert:
         1. Data type returned is datetime.datetime 
         2. Format '%Y-%m-%d %H:%M:%S.%s'
      """
      get_timestamp(self.que)
      result=self.que.get()
      assert type(result) == datetime.datetime 
      try: 
         datetime.datetime.strptime(str(result), '%Y-%m-%d %H:%M:%S.%s')
      except: 
         return False
      return True

   def test_cpu_insight(self): 
      """
      Test cpu_insight
      :assert: 
         1. List of keys 
         2. Value in each is float 
      """
      cpu_insight(self.que)
      result=self.que.get()
      assert sorted(list(result.keys())) == ['cpu_0', 'idle', 'iowait', 'system']
      for key in list(result.keys()): 
         assert type(result[key]) == float

   def test_mem_insight(self): 
      """
      Test mem_insight
      :assert:
         1. List of keys 
         2. Value type 
         3. If precent > 90 --> warning = True
      """
      mem_insight(self.que)
      result=self.que.get() 
      assert sorted(list(result.keys())) == ['percent', 'warning']
      assert type(result['percent']) == float 
      assert type(result['warning']) == bool 
      if result['percent'] > 90: 
         assert result['warning'] == True 
      else: 
         assert result['warning'] == False

   def test_disk_insight(self): 
      """
      Test disk_insight
      :assert:
         1. List of keys 
         2. Value type 
         3. If useage > 75.55 --> warning=True 
      """
      disk_insight(self.que)
      result=self.que.get() 
      # {'read': 15656, 'warning': False, 'write': 6228, 'useage': 28.1}
      assert sorted(list(result.keys())) == ['read', 'useage', 'warning', 'write']
      for key in result.keys():
         if key != 'warning' and key != 'useage': 
            assert type(result[key]) == int
      assert type(result['useage']) == float 
      assert type(result['warning']) == bool 
      if result['useage'] > 75.55: 
         assert result['warning'] == True 
      else: 
         assert result['warning'] == False 

   def test_process(self): 
      """
      Test process from generating data to sending it into file
      :assert: 
         1. get_data() - Data types returned are valid
         2. create_json() - Data inserted into JSON 
      """    
      timestamp, cpu_data, mem_data, disk_data = get_data() 
      assert type(timestamp) == datetime.datetime 
      assert type(cpu_data) == dict
      assert type(mem_data) == dict 
      assert type(disk_data) == dict 

      json_objects=create_json(timestamp, cpu_data, 'cpu')
      result=json.loads(json_objects)     
      assert sorted(list(result.keys())) == ['asset', 'key', 'readings', 'timestamp']
      assert result['asset'] == 'system/cpu' 
      assert type(result['readings']) == dict 

      actual=result['readings']
      for key in ['cpu_0', 'idle', 'iowait', 'system']:
         assert actual[key] == cpu_data[key]
      try:  
         uuid.UUID(result['key'])
      except: 
         return False 
      else: 
         return True 
      try:
         datetime.datetime.strptime(str(result['timestamp']), '%Y-%m-%d %H:%M:%S.%s')
      except:
         return False
      return True

   def test_main(self): 
      """
      Test create file process 
      :assert: 
         File gets created 
      """
      main() 
      actual=int(os.popen('ls /tmp/*.json | wc -l').read().split('\n')[0])
      assert actual == 1
