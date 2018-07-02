#!/bin/user/python
"""
Name: Ori Shadmon
Date: June 2018 
Description: The following code takes GitHub connection info, and generates traffic, commits, and clones insight. 
             This data is stored in JSON files under /tmp
"""

import argparse
import datetime
import json
import os
import requests
import uuid

def send_request(repo:str='', organization:str='', auth_pair:tuple=())->(requests.models.Response, requests.models.Response, requests.models.Response): 
   """
   Send request to specific Github API endpoint
   :param:
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


   return traffic_response, commits_response, clones_response
  

def read_traffic(traffic:requests.models.Response=None, repo:str='repo_name'): 
   """
   Write daily traffic to file 
   :param: 
      traffic:requests.models.Response - Object with traffic info
      repo:str - repository name 
   :sample: 
   {
        "timestamp" : "2018-06-08T00:00:00Z"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/traffic"
        "readings"  : {"traffic"" : 18}
   }
   """
   traffic=traffic.json()
   output=[]
   open('/tmp/github_%s_traffic_data.json' % repo, 'w').close()
   f=open('/tmp/github_%s_traffic_data.json' % repo, 'w')
   for key in traffic['views']: 
      timestamp=datetime.datetime.strptime(key['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
      data=json.dumps({'timestamp' : str(timestamp), 
                       'key'       : str(uuid.uuid1()),
                       'asset'     : 'github/%s/traffic' % repo, 
                       'readings'  : {'traffic' : key['uniques']}
                     })
      f.write(data)
      f.write("\n")
   f.close()

def read_commits_timestamp(commits:requests.models.Response=None, repo:str='repo_name'): 
   """
   Write daily commits to file - brokenup by timestamp  
   :param: 
      commits:requests.models.Response - Object with commit info
      repo:str - repository name
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
   open('/tmp/github_%s_commits_timestamp_data.json' % repo, 'w').close() 
   f=open('/tmp/github_%s_commits_timestamp_data.json' % repo, 'w') 
   for key in timestamps: 
      data=json.dumps({'timestamp' : str(key),
                       'key'       : str(uuid.uuid1()),
                       'asset'     : 'github/%s/commits/timestamp' % repo, 
                       'readings'  : {'commits/timestamp' : timestamps[key]}
                     })
      f.write(data)
      f.write("\n")
   f.close()

def read_commits_users(commits:requests.models.Response=None, repo:str='repo_name'): 
   """
   Write commits to file - brokenup by users 
   :param: 
      commitsrequests.models.Response=None - Object with commit info
      repo:str - repository name
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
   for i in range(len(commits)): 
      user=commits[i]['commit']['author']['name']
      if user not in users: 
         users[user]=0
      users[user]+=1

   # Create file with JSON objects based on users dict
   open('/tmp/github_%s_commits_user_data.json' % repo, 'w').close() 
   f=open('/tmp/github_%s_commits_user_data.json' % repo, 'w')
   # number of users commit  
   data=json.dumps({'timestamp' : str(datetime.datetime.now()),    
                    'key'       : str(uuid.uuid1()),
                    'asset'     : 'github/%s/commits/users' % repo, 
                    'readings'   : {'commits/users' : int(len(users))}
                  })
   f.write(data)
   f.write('\n')
   # number of commits per user 
   for key in users: 
      data=json.dumps({'timestamp' : str(datetime.datetime.now()), 
                       'key'       : str(uuid.uuid1()),
                       'asset'     : 'github/%s/commits/users/%s' % (repo, key.replace(' ','-').replace('_', '-')),
                       'readings' : {'commits/users/%s' % key.replace(' ','-').replace('_', '-') : users[key]}
                     }) 
      f.write(data)
      f.write("\n")
   f.close() 

def read_clones(clones:requests.models.Response=None, repo:str='repo_name'): 
   """
   Write daily clones to file
   :param: 
      clones:requests.models.Response - Object with clones info 
      repo:str - repository name
   :sample: 
   {
        "timestamp" : "2018-06-08T00:00:00Z"
        "key"       : "ff7a5466-7c0a-11e8-ab26-0800275d93ce"
        "asset"     : "github/repo_name/clones"
        "readings" : {"clones" : 5}
   }
   """
   clones=clones.json()
   output=[]
   open('/tmp/github_%s_clones_data.json' % repo, 'w').close()
   f=open('/tmp/github_%s_clones_data.json' % repo, 'w')
   for key in clones['clones']:
      timestamp=datetime.datetime.strptime(key['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
      data=json.dumps({'timestamp' : str(key['timestamp']),
                       'key'       : str(uuid.uuid1()),
                       'asset'     : 'github/%s/clones' % repo,
                       'readings'  : {'clones' : key['uniques']}
                     })
      f.write(data)
      f.write("\n")
   f.close()

   
def main():
    """
    Main
    :positional arguments:
        auth_file   authentication file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('auth_file', default='$HOME/foglamp-south-plugin/GitHub_Data_Generator/other/auth_pair.txt', help='authentication file')
    args = parser.parse_args()
    env=os.path.expanduser(os.path.expandvars(args.auth_file))
    with open(env, 'r') as f:
       output=f.read().replace('\n','').split(' ')
    auth=(str(output[0].split(':')[0]), str(output[0].split(':')[-1]))
    repo=output[1]
    org=output[2]

    traffic_response, commits_response, clones_response=send_request(repo, org, auth)

    read_traffic(traffic_response, repo)
    read_clones(clones_response, repo)
    read_commits_timestamp(commits_response, repo) 
    read_commits_users(commits_response, repo)

if __name__ == '__main__': 
   main()
