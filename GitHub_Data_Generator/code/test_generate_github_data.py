import asyncio
import datetime 
import json 
import os 
import queue 
import random
import requests
import sys 
import threading
import time
import uuid

import generate_github_data

# Code requires foglamp\_dir (under '$HOME/FogLAMP') and foglamp_south_http (under '$HOME/foglamp-south-http')
foglamp_dir=os.path.expanduser(os.path.expandvars('$HOME/foglamp-south-plugin/FogLAMP'))
sys.path.insert(0, foglamp_dir)
from foglamp import FogLAMP

class TestGitHubData: 
   def setup_method(self): 
      """
      Given authentication file (auth_pair.txt), prepare config information
      Note that auth_pair should be under $HOME and with valid info for tests to succeed.
      :param: 
         self.auth - user:password of GitHub 
         self.repo - repo testing against 
         self.org - organization repo is under 
         self.json_dir - dir to store JSON data 
      """
      env=os.path.expanduser(os.path.expandvars('$HOME/auth_pair.txt'))
      with open(env, 'r') as f:
         output=f.read().replace('\n', '').split(' ') 
      self.auth=(str(output[0].split(':')[0]), str(output[0].split(':')[-1]))
      self.repo=output[1]
      self.org=output[2] 
      self.json_dir='/tmp'
      self.foglamp=FogLAMP() 
      os.system('rm -rf %s/*.json' % self.json_dir)

   def teardown_method(self): 
      """
      Remove data in self.json_dir
      """
      os.system('rm -rf %s/*.json') 

   def __main(self, process:str='traffic')->(requests.models.Response, str):
      """
      Execute "main" like behavior for get_timestamp, send_request to simply testing. 
      :param: 
         process:str - process you want to return (traffic, commits, clones)
      :return:
         timestamp (str) and requests.models.Response based on process
      """
      timestamp_que=queue.Queue()
      traffic_que=queue.Queue()
      commits_que=queue.Queue()
      clones_que=queue.Queue()
      threads=[threading.Thread(target=generate_github_data.get_timestamp, args=(timestamp_que,)),
               threading.Thread(target=generate_github_data.send_request,  args=(traffic_que, commits_que, clones_que, self.repo, self.org, self.auth,))
              ]
   
      for thread in threads:
         thread.start()
      for thread in threads:
         thread.join()
      timestamp=timestamp_que.get()
      traffic_request=traffic_que.get()
      commits_request=commits_que.get()
      clones_request=clones_que.get()

      if process.lower() == 'traffic': 
         return traffic_request, timestamp
      if process.lower() == 'commits': 
         return commits_request, timestamp
      if process.lower() == 'clones': 
         return clones_request, timestamp

   def test_get_timestamp(self): 
      """
      Test get_timestamp method
      :assert: 
         Method returns today's date formated as %Y_%m_%d
      """
      que=queue.Queue() 
      generate_github_data.get_timestamp(que)
      timestamp=que.get()
      assert timestamp == datetime.datetime.now().strftime('%Y_%m_%d')

   def test_send_request(self): 
      """
      Test send_requests
      :assert: 
         Method retrives valid status codes
      """
      traffic_que=queue.Queue()
      commits_que=queue.Queue()
      clones_que=queue.Queue()

      generate_github_data.send_request(traffic_que, commits_que, clones_que, self.repo, self.org, self.auth)

      traffic=traffic_que.get()
      commits=commits_que.get()
      clones=clones_que.get()
      
      for code in [traffic.status_code, commits.status_code, clones.status_code]:
         assert code == 200


   def test_read_traffic(self): 
      """
      Test read_traffic 
      :assert:
         1. returns a list 
         2. a random set in list is dictionary with valid data
      """
      traffic_request, timestamp = self.__main('traffic')
      data=generate_github_data.read_traffic(traffic_request, self.repo, timestamp)
      assert type(data) == list
      data_set=random.choice(data)
      assert type(data_set) == dict
      assert sorted(data_set.keys()) == ['asset', 'key', 'readings', 'timestamp']
      assert data_set['asset'] == 'github/FogLAMP/traffic' 
      assert list(data_set['readings'].keys()) == ['traffic']
      try:
         uuid.UUID(data_set['key'], version=4)
      except:
         return False

   def test_read_commits_timestamp(self): 
      """
      Test read_commits_timestamp
      :assert: 
         1. returns a list 
         2. a random set in list is dictiionary with valid data 
      """
      commits_request, timestamp = self.__main('commits')
      data=generate_github_data.read_commits_timestamp(commits_request, self.repo, timestamp)
      assert type(data) == list
      data_set=random.choice(data)
      assert type(data_set) == dict 
      assert sorted(data_set.keys()) == ['asset', 'key', 'readings', 'timestamp']
      assert data_set['asset'] == 'github/FogLAMP/commits/timestamp' 
      assert list(data_set['readings'].keys()) == ['commits/timestamp']
      try:
         uuid.UUID(data_set['key'], version=4)
      except:
         return False

   def test_send_json(self):
      """
      Test cases where data gets sent to JSON
      :assert: 
         1. Assert data gets returned 
         2. Data retuened can be converted to JSON  
      """
      traffic_request, timestamp = self.__main('traffic')
      traffic_data=generate_github_data.read_traffic(traffic_request, self.org, timestamp) 
      file_name='/tmp/test_output.json'
      open(file_name, 'w').close()
      generate_github_data.write_to_file(file_name, traffic_data)
      with open(file_name, 'r') as f: 
         lines=f.read().split('\n')
      del lines[-1]
      assert len(lines) > 0
      for line in lines: 
         try: 
            json.loads(line)
         except: 
            return False
         else: 
            return True
    

   def test_send_foglamp(self): 
      """
      Test cases where data gets sent to FogLAMP
      :assert:
         By executing CURL and geting a value assert timestamp info has been posted
      """
      self.foglamp.stop_foglamp() 
      self.foglamp.reset_foglamp() 
      self.foglamp.start_foglamp() 
      traffic_request, timestamp = self.__main('traffic')
      traffic_data=generate_github_data.read_traffic(traffic_request, self.org, timestamp)
      loop = asyncio.get_event_loop()
      loop.run_until_complete(generate_github_data.send_to_foglamp(traffic_data, 'localhost', 6683))
      time.sleep(10)

      url='http://localhost:8081/foglamp/asset'
      res = requests.get(url)
      result=res.json() 
      assert len(result) == 1
      
      self.foglamp.stop_foglamp()
      self.foglamp.reset_foglamp()

