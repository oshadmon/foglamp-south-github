"""
Name: Ori Shadmon
Date: June 2018 
Description: The following code takes GitHub connection info, and generates traffic, commits, and clones insight. 
             This data is stored in JSON files under /tmp
"""

import argparse
import datetime
import json
import requests

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

   # Commits 
   commits_url = base_url + organization + '/' + repo + '/commits' 
   commits_response = requests.get(commits_url, auth=auth_pair)

   # Clones 
   base_url = 'https://api.github.com/repos/'
   base_url = base_url + organization + '/' + repo + '/traffic/clones'
   clones_response = requests.get(base_url, auth=auth_pair)


   return traffic_response, commits_response, clones_response
  

def read_traffic(traffic:requests.models.Response=None): 
   """
   Write daily traffic to file 
   :param: 
      traffic:requests.models.Response - Object with traffic info
   :sample: 
   {
        "timestamp"     : "2018-06-08T00:00:00Z"
        "asset"         : "traffic"
        "sensor_values" : {"uniques" : 18}
   }
   """
   traffic=traffic.json()
   output=[]
   open('/tmp/github_traffic_data.json', 'w').close()
   f=open('/tmp/github_traffic_data.json', 'w')
   for key in traffic['views']: 
      timestamp=datetime.datetime.strptime(key['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
      data=json.dumps({'timestamp'    : str(timestamp), 
                       'asset'        : 'github/traffic', 
                       'sensor_values' : {'unique' : key['uniques']}
                     })
      f.write(data)
      f.write("\n")
   f.close()

def read_commits_timestamp(commits:requests.models.Response=None): 
   """
   Write daily commits to file - brokenup by timestamp  
   :param: 
      commits:requests.models.Response - Object with commit info
   :sample: 
   {
        "timestamp"     : "2018-06-18"
        "asset"         : "github/commits/timestamp"
        "sensor_values" : {"uniques" : 12}
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
   open('/tmp/github_commits_timestamp_data.json', 'w').close() 
   f=open('/tmp/github_commits_timestamp_data.json', 'w') 
   for key in timestamps: 
      data=json.dumps({'timestamp'     : str(key),
                       'asset'         : 'github/commits/timestamp', 
                       'sensor_values' : {'unique' : timestamps[key]}
                     })
      f.write(data)
      f.write("\n")
   f.close()

def read_commits_users(commits:requests.models.Response=None): 
   """
   Write commits to file - brokenup by users 
   :param: 
      commitsrequests.models.Response=None - Object with commit info
   :sample: 
   {
        "timestamp"     : "2018-06-21 15:30:09.537268"
        "asset"         : "github/commits/users/Ivan_Zoratti"
        "sensor_values" : {"unique" : 2}
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
   open('/tmp/github_commits_user_data.json', 'w').close() 
   f=open('/tmp/github_commits_user_data.json', 'w')
   for key in users: 
      data=json.dumps({'timestamp'     : str(datetime.datetime.now()), 
                       'asset'         : 'github/commits/users/%s' % key.replace(' ','-').replace('_', '-'),
                       'sensor_values' : {'unique' : users[key]}
                     }) 
      f.write(data)
      f.write("\n")
   f.close() 

def read_clones(clones:requests.models.Response=None): 
   """
   Write daily clones to file
   :param: 
      clones:requests.models.Response - Object with clones info 
   :sample: 
   {
        "timestamp"     : "2018-06-08T00:00:00Z"
        "asset"         : "traffic"
        "sensor_values" : {"uniques" : 5}
   }
   """
   clones=clones.json()
   output=[]
   open('/tmp/github_clones_data.json', 'w').close()
   f=open('/tmp/github_clones_data.json', 'w')
   for key in clones['clones']:
      timestamp=datetime.datetime.strptime(key['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
      data=json.dumps({'timestamp'    : str(key['timestamp']),
                       'asset'        : 'github/clones',
                       'sensor_values' : {'uniques' : key['uniques']}
                     })
      f.write(data)
      f.write("\n")
   f.close()

   
def main():
    """
    Main
    :positional arguments:
       username              Github username
       repo                  User's repo

    :optional arguments:
       -h, --help            show this help message and exit
       -o ORGANIZATION, --organization ORGANIZATION Github organization
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='Github username')
    parser.add_argument('repo', help='User\'s repo', default='ALL', nargs='?')
    parser.add_argument('-o', '--organization', default=None, help='Github organization')
    args = parser.parse_args()

    # Set Variables 
    str = args.username.strip()
    sub = str.split(':', 1 )
    len_sub = len(sub)
    username = sub[0].strip()
    if len_sub > 1:
        pw = sub[1].strip()
    else:
        pw = getpass.getpass('Password:')
    auth_pair = (username, pw)
    repo = args.repo.strip()
    organization = username
    if args.organization != None:
       organization = args.organization.strip()

    traffic_response, commits_response, clones_response=send_request(repo, organization, auth_pair)

    read_traffic(traffic_response)
    read_clones(clones_response)
    read_commits_timestamp(commits_response) 
    read_commits_users(commits_response)

if __name__ == '__main__': 
   main()
