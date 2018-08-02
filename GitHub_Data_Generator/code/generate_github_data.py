#!/bin/user/python
"""
Name: Ori Shadmon
Date: June 2018 
Description: The following code takes GitHub connection info, and generates traffic, commits, and clones insight. 
             This data is stored in JSON files under /tmp
"""
import aiohttp
import argparse
import asyncio
import datetime
import json
import os
import queue
import requests
import threading
import uuid

loop = asyncio.get_event_loop()

def get_timestamp(que:queue.Queue=None)->str:
   """
   Create a current timestamp
   """
   timestamp=datetime.datetime.now() 
   timestamp=timestamp.strftime('%Y_%m_%d')
   que.put(timestamp)

def send_request(traffic_que:queue.Queue=None, commits_que:queue.Queue=None, clones_que:queue.Queue()=None,  repo:str='', organization:str='', 
                 auth_pair:tuple=())->(requests.models.Response, requests.models.Response, requests.models.Response): 
   """
   Send request to specific Github API endpoint
   :param:
      traffic_que:queue.Queue - que to store traffic results 
      commits_que:queue.Queue - que to store commits reults 
      clones_que:queue.Queue - que to store clones results 
      repo:str - repository name
      organization:str - organization name 
      auth_pair:tuple - user/password tuple pair
   :return: 
      request response for traffic, commits, and clones
   """

   # Traffic 
   base_url = 'https://api.github.com/repos/'
   traffic_url = base_url + organization + '/' + repo + '/traffic/views'
   traffic_response = requests.get(traffic_url, auth=auth_pair)

   if traffic_response.status_code != 200: 
      print("Error %s: %s " % (traffic_response.status_code, traffic_response.json()['message']))
      exit(1)

   # Commits 
   commits_url = base_url + organization + '/' + repo + '/commits' 
   commits_response = requests.get(commits_url, auth=auth_pair)

   # Clones 
   base_url = 'https://api.github.com/repos/'
   base_url = base_url + organization + '/' + repo + '/traffic/clones'
   clones_response = requests.get(base_url, auth=auth_pair)

   traffic_que.put(traffic_response) 
   commits_que.put(commits_response)
   clones_que.put(clones_response)
  

def read_traffic(traffic:requests.models.Response=None, repo:str='repo_name', timestamp:str=datetime.datetime.now().strftime('%Y_%m_%d'))->list:
   """
   Create list of JSON objects with traffic info, and send to FogLAMP  
   :param: 
      traffic:requests.models.Response - Object with traffic info
      repo:str - repository name 
      json_dir:str - directory that will store json object
      timestamp:str - date when data is generated
      host:str - FogLAMP POST host 
      port:int - FogLAMP POST port 
   :sample: 
   {
        "timestamp" : "2018-06-08T00:00:00Z"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/traffic"
        "readings"  : {"traffic"" : 18}
   }
   """
   traffic=traffic.json()
   data=[]
   for key in traffic['views']: 
      timestamp=datetime.datetime.strptime(key['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
      data.append(json.dumps({'timestamp' : str(timestamp), 
                              'key'       : str(uuid.uuid1()),
                              'asset'     : 'github/%s/traffic' % repo, 
                              'readings'  : {'traffic' : key['uniques']}
                            }))
   return data

def read_commits_timestamp(commits:requests.models.Response=None, repo:str='repo_name', timestamp:str=datetime.datetime.now().strftime('%Y_%m_%d'))->list:
   """
   Create list of JSON objects with commits (by timestamp) info, and send to FogLAMP 
   :param: 
      commits:requests.models.Response - Object with commit info
      repo:str - repository name
      json_dir:str - directory that will store json object
      timestamp:str - date when data is generated
   :sample: 
   {
        "timestamp" : "2018-06-18"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/commits/timestamp"
        "readings"  : {"commits/timestamp" : 12}
   }
   """
   commits=commits.json()

   # Group by TIMESTAMP
   timestamps={} 
   for i in range(len(commits)): 
      timestamp=commits[i]['commit']['author']['date']
      timestamp=datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
      if timestamp not in timestamps: 
         timestamps[timestamp]=0 
      timestamps[timestamp]+=1 

   # Create file with JSON object based on timestamps dict 
   data=[]
   for key in timestamps: 
      data.append(json.dumps({'timestamp' : str(key),
                              'key'       : str(uuid.uuid1()),
                              'asset'     : 'github/%s/commits/timestamp' % repo, 
                              'readings'  : {'commits/timestamp' : timestamps[key]}
                            }))
   return data 

def read_commits_users(commits:requests.models.Response=None, repo:str='repo_name', timestamp:str=datetime.datetime.now().strftime('%Y_%m_%d'))->list:
   """
   Create list of JSON objects with commits (by user) info, and send to FogLAMPe
   :param: 
      commitsrequests.models.Response=None - Object with commit info
      repo:str - repository name
      json_dir:str - directory that will store json object
      timestamp:str - date when data is generated
   :sample: 
   {
        "timestamp" : "2018-06-21 15:30:09.537268"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/commits/users/Ivan_Zoratti"
        "readings"  : {"commits/users/Ivan_Zoratti" : 2}
   }
   """
   commits=commits.json()
   users={} 
   data=[]
   for i in range(len(commits)): 
      user=commits[i]['commit']['author']['name']
      if user not in users: 
         users[user]=0
      users[user]+=1

   data.append(json.dumps({'timestamp' : str(datetime.datetime.now()),    
                           'key'       : str(uuid.uuid1()),
                           'asset'     : 'github/%s/commits/users' % repo, 
                           'readings'   : {'commits/users' : int(len(users))}
                         }))
   # number of commits per user 
   for key in users: 
      data.append(json.dumps({'timestamp' : str(datetime.datetime.now()), 
                              'key'       : str(uuid.uuid1()),
                              'asset'     : 'github/%s/commits/users/%s' % (repo, key.replace(' ','-').replace('_', '-')),
                              'readings' : {'commits/users/%s' % key.replace(' ','-').replace('_', '-') : users[key]}
                            })) 
   return data

def read_clones(clones:requests.models.Response=None, repo:str='repo_name', timestamp:str=datetime.datetime.now().strftime('%Y_%m_%d'))->list: 
   """
   Create list of JSON objects with daily clones, and write to file 
   :param: 
      clones:requests.models.Response - Object with clones info 
      repo:str - repository name
      json_dir:str - directory that will store json object
      timestamp:str - date when data is generated
   :sample: 
   {
        "timestamp" : "2018-06-08T00:00:00Z"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/clones"
        "readings" : {"clones" : 5}
   }
   """
   clones=clones.json()
   data=[]
   for key in clones['clones']:
      timestamp=datetime.datetime.strptime(key['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
      data.append(json.dumps({'timestamp' : str(key['timestamp']),
                              'key'       : str(uuid.uuid1()),
                              'asset'     : 'github/%s/clones' % repo,
                              'readings'  : {'clones' : key['uniques']}
                            }))
   return data 

async def send_to_foglamp(data:list=[], arg_host:str='localhost', arg_port:int=6683): 
   """
   POST to FogLAMP using HTTP
   :args: 
      data:list - list of JSON objects
      arg_host:str - FogLAMP Host 
      arg_port:int - FogLAMP POST port 
   """  
   headers = {'content-type': 'application/json'}
   url = 'http://{}:{}/sensor-reading'.format(arg_host, arg_port)
   for payload in data: 
      async with aiohttp.ClientSession() as session:
         async with session.post(url, data=payload, headers=headers) as resp:
            await resp.text()
            status_code = resp.status
            if status_code in range(400, 500):
               print("Bad request error | code:{}, reason: {}".format(status_code, resp.reason))
               exit(1)
            if status_code in range(500, 600):
               print("Server error | code:{}, reason: {}".format(status_code, resp.reason))
               exit(1)

def write_to_file(file_name:str='/tmp/data.json', data:list=[]):
   """
   Write data into JSON file 
   :args: 
      file_name:str - File to store JSON data into 
      data:list - list of JSON objects
   """
   with open(file_name, 'a') as f:
      for obj in data:
         f.write(obj)
         f.write('\n')

def main():
    """
    Main
    :positional arguments:
       auth_file             authentication file
       host                  FogLAMP POST Host
       port                  FogLAMP POST Port

    :optional arguments:
       -h, --help            show this help message and exit
       -s SEND, --send SEND  Where to send the data to (foglamp|json|both)
       -d DIR, --dir DIR     directory to send data into (for JSON)

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('auth_file', default='$HOME/foglamp-south-plugin/GitHub_Data_Generator/other/auth_pair.txt', help='authentication file')
    parser.add_argument('host', default='localhost', help='FogLAMP POST Host')
    parser.add_argument('port', default=6683, help='FogLAMP POST Port')
    parser.add_argument('-s', '--send', default='foglamp', help='Where to send the data to (foglamp|json|both)')
    parser.add_argument('-d', '--dir', default='/tmp', help='directory to send data into (for JSON)')
    args = parser.parse_args()

    env=os.path.expanduser(os.path.expandvars(args.auth_file))
    with open(env, 'r') as f:
       output=f.read().replace('\n','').split(' ')
    auth=(str(output[0].split(':')[0]), str(output[0].split(':')[-1]))
    repo=output[1]
    org=output[2]
    json_dir=output[3]

    # Generate data 
    timestamp_que=queue.Queue()
    traffic_que=queue.Queue()
    commits_que=queue.Queue()
    clones_que=queue.Queue()
    threads=[threading.Thread(target=get_timestamp, args=(timestamp_que,)), 
             threading.Thread(target=send_request,  args=(traffic_que, commits_que, clones_que, repo, org, auth,))
            ]    
    for thread in threads:
       thread.start()
    for thread in threads:
       thread.join()
    timestamp=timestamp_que.get()
    traffic_request=traffic_que.get() 
    commits_request=commits_que.get() 
    clones_request=clones_que.get() 

    traffic_data=read_traffic(traffic_request, repo, timestamp) 
    commits_timestamp_data=read_commits_timestamp(commits_request, repo, timestamp)
    commits_users_data=read_commits_users(commits_request, repo, timestamp) 
    clones_data=read_clones(clones_request, repo, timestamp) 
    
    file_name=args.dir+'/%s_github_%s_data.json' % (datetime.datetime.now().strftime('%Y_%m_%d'), repo) 
    loop = asyncio.get_event_loop()
    if args.send.lower() == 'foglamp': # Send to FogLAMP 
       loop.run_until_complete(send_to_foglamp(traffic_data, args.host, args.port)) 
       loop.run_until_complete(send_to_foglamp(commits_timestamp_data, args.host, args.port))
       loop.run_until_complete(send_to_foglamp(commits_users_data, args.host, args.port))
       loop.run_until_complete(send_to_foglamp(clones_data, args.host, args.port))
    elif args.send.lower() == 'json': # Send to JSON file
       open(file_name, 'w').close()
       write_to_file(file_name, traffic_data)
       write_to_file(file_name, commits_timestamp_data)
       write_to_file(file_name, commits_users_data) 
       write_to_file(file_name, clones_data)
    else: # If something else write to both
       loop.run_until_complete(send_to_foglamp(traffic_data, args.host, args.port))
       loop.run_until_complete(send_to_foglamp(commits_timestamp_data, args.host, args.port))
       loop.run_until_complete(send_to_foglamp(commits_users_data, args.host, args.port))
       loop.run_until_complete(send_to_foglamp(clones_data, args.host, args.port))
       open(file_name, 'w').close()
       write_to_file(file_name, traffic_data)
       write_to_file(file_name, commits_timestamp_data)
       write_to_file(file_name, commits_users_data)
       write_to_file(file_name, clones_data)

  

if __name__ == '__main__': 
   main()