import json
import os 
import random
import requests
from generate_json_files import send_request, read_traffic, read_clones, read_commits_timestamp, read_commits_users

class TestGenerateJSON: 
   def setup_method(self): 
      """
      setup method
      :param: 
         repo:str - repo to look into
         org:str - organization repo falls under 
         auth:str - authentication pair
         env:str - file containing authentication pair [user:password]
      """    
      # Params
      repo='foglamp' 
      org='FogLAMP'
      env=os.path.expanduser(os.path.expandvars('$HOME/auth_pair.txt')) 
      with open(env, 'r') as f: 
         auth=str(f.readlines()[0])
      user=str(auth.split(':')[0])
      passwd=str(auth.split(':')[-1].split("\n")[0])
      auth=(user, passwd) 

      # Clean env 
      self.__clean_env() 
      # Prepare requests
      self.traffic_response, self.commits_response, self.clones_response = send_request(repo, org, auth)


   def teardown_method(self): 
      """
      teardown
      """
      self.__clean_env()
     
   def __clean_env(self): 
      """
      Remove json data 
      """
      os.system("rm -rf /tmp/*.json") 

   def test_send_request(self): 
      """
      Test send_request
      :assert: 
         1. send_request returns requests.models.Response objects 
         2. requests.models.Response status code is 200 (meaning passed) 
      """

      assert type(self.traffic_response) == requests.models.Response
      assert self.traffic_response.status_code == 200

      assert type(self.commits_response) == requests.models.Response
      assert self.commits_response.status_code == 200

      assert type(self.clones_response)  == requests.models.Response
      assert self.clones_response.status_code == 200


   def test_read_traffic(self): 
      """
      Test read_traffic
      :assert: 
         1. File gets created 
         2. 1-14 rows 
         3. At random check keys in json object
      """ 
      file_check_stmt="ls /tmp/github_traffic_data.json | wc -l"
      file_count="cat /tmp/github_traffic_data.json | wc -l" 
      
      # Check file gets created 
      file_check=int(os.popen(file_check_stmt).read().split("\n")[0])
      assert file_check == 0
      read_traffic(self.traffic_response)  
      file_check=int(os.popen(file_check_stmt).read().split("\n")[0])
      assert file_check == 1 

      # Check rows are inserted 
      row_count=int(os.popen(file_count).read().split('\n')[0])
      assert row_count >= 1 and row_count <= 15

      # Get Data 
      data=[] 
      with open('/tmp/github_traffic_data.json') as f: 
         for line in f.readlines():
            data.append(json.loads(line))

      # Assert keys in each data type
      keys=['asset', 'sensor_values', 'timestamp']
      for group in data: 
         assert sorted(list(group.keys())) == keys # Validate keys
         
      # Assert that for a random JSON object value types are valid
      data_id=random.randint(0, len(data)-1) 
      assert data[data_id]['asset'] == 'github/traffic'
      try: 
         datetime.datetime.strptime(data[data_id]['timestamp'], '%Y-%m-%d %H:%M:%S')
      except: 
         return False
      assert type(data[data_id]['sensor_values']) == dict 
      assert type(data[data_id]['sensor_values']['unique']) == int


   def test_read_clones(self): 
      """
      Test read_clones
      :assert: 
         1. Fle gets created 
         2. Row count 
         3. At random check keys in json object
      """
      file_check_stmt="ls /tmp/github_clones_data.json | wc -l"
      file_count="cat /tmp/github_clones_data.json | wc -l"

      file_check=int(os.popen(file_check_stmt).read().split("\n")[0])
      assert file_check == 0
      read_clones(self.clones_response)
      file_check=int(os.popen(file_check_stmt).read().split("\n")[0])
      assert file_check == 1

      # Check rows are inserted 
      row_count=int(os.popen(file_count).read().split('\n')[0])
      assert row_count >= 1 and row_count <= 15

      # Get Data 
      data=[]
      with open('/tmp/github_clones_data.json') as f:
         for line in f.readlines():
            data.append(json.loads(line))

      # Assert keys in each data type
      keys=['asset', 'sensor_values', 'timestamp']
      for group in data:
         assert sorted(list(group.keys())) == keys # Validate keys

      # Assert that for a random JSON object value types are valid
      data_id=random.randint(0, len(data)-1)
      assert data[data_id]['asset'] == 'github/clones'
      try:
         datetime.datetime.strptime(data[data_id]['timestamp'], '%Y-%m-%d %H:%M:%S')
      except:
         return False
      assert type(data[data_id]['sensor_values']) == dict
      assert type(data[data_id]['sensor_values']['unique']) == int

   def test_read_commits_timestamp(self): 
      """
      Test read_commits_timestamp
      :assert: 
         1. File gets created 
         2. Row count 
         3. At random check keys in json object 
      """
      file_check_stmt="ls /tmp/github_commits_timestamp_data.json | wc -l"
      file_count="cat /tmp/github_commits_timestamp_data.json | wc -l"
      file_check=int(os.popen(file_check_stmt).read().split("\n")[0])
      assert file_check == 0
      read_commits_timestamp(self.commits_response)
      file_check=int(os.popen(file_check_stmt).read().split("\n")[0])
      assert file_check == 1

      # Check rows are inserted 
      row_count=int(os.popen(file_count).read().split('\n')[0])
      assert row_count >= 1 # Verify that clone has been done 

      data=[]
      with open('/tmp/github_commits_timestamp_data.json') as f:
         for line in f.readlines():
            data.append(json.loads(line))

      # Assert keys in each data type
      keys=['asset', 'sensor_values', 'timestamp']
      for group in data:
         assert sorted(list(group.keys())) == keys # Validate keys

      # Assert that for a random JSON object value types are valid
      data_id=random.randint(0, len(data)-1)
      assert data[data_id]['asset'] == 'github/commits/timestamp'
      try:
         datetime.datetime.strptime(data[data_id]['timestamp'], '%Y-%m-%d %H:%M:%S')
      except:
         return False
      assert type(data[data_id]['sensor_values']) == dict
      assert type(data[data_id]['sensor_values']['unique']) == int

   def test_read_commits_users(self):
      """
      Test read_commits_users
      :assert:
         1. File gets created 
         2. Row Count 
         3. At random check keys in JSON object
      """
      file_check_stmt="ls /tmp/github_commits_user_data.json | wc -l"
      file_count="cat /tmp/github_commits_user_data.json | wc -l"

      file_check=int(os.popen(file_check_stmt).read().split("\n")[0])
      assert file_check == 0
      read_commits_users(self.commits_response)
      file_check=int(os.popen(file_check_stmt).read().split("\n")[0])
      assert file_check == 1

      data=[]
      with open('/tmp/github_commits_user_data.json') as f:
         for line in f.readlines():
            data.append(json.loads(line))

      keys=['asset', 'sensor_values', 'timestamp']
      for group in data:
         assert sorted(list(group.keys())) == keys # Validate keys

      # Assert that for a random JSON object value types are valid
      data_id=random.randint(0, len(data)-1)
      assert data[data_id]['asset'] == 'github/commits/users/%s' % data[data_id]['asset'].split("/")[-1]
      try:
         datetime.datetime.strptime(data[data_id]['timestamp'], '%Y-%m-%d %H:%M:%S')
      except:
         return False
      assert type(data[data_id]['sensor_values']) == dict
      assert type(data[data_id]['sensor_values']['unique']) == int
