# foglamp-south-github
The following scripts take data from different components (such as _GitHub_ and _Google Analytics_), and send it into [FogLAMP](https://github.com/foglamp/FogLAMP).  


# What is FogLAMP:
[FogLAMP](https://github.com/foglamp/FogLAMP) is an open source platform for the **Internet of Things**, and an essential component in **Fog Computing**. It uses a modular **microservices architecture** including sensor data collection, storage, processing and forwarding to historians, Enterprise systems and Cloud-based services. FogLAMP can run in highly available, stand alone, unattended environments that assume unreliable network connectivity.
.

# Scripts 

`GitHub_Data_Generator` - The following is based on [github-traffic-stats](https://github.com/nchah/github-traffic-stats), retrieving data from GitHub and send it to FogLAMP. 
```
# Help 
~/foglamp-south-plugin$ python3 GitHub_Data_Generator/code/generate_github_data.py --help 
usage: generate_github_data.py [-h] [-s SEND] [-d DIR] auth_file host port

positional arguments:
  auth_file             authentication file
  host                  FogLAMP POST Host
  port                  FogLAMP POST Port

optional arguments:
  -h, --help            show this help message and exit
  -s SEND, --send SEND  Where to send the data to (foglamp|json|both)
  -d DIR, --dir DIR     directory to send data into (for JSON)

# Send to JSON 
~/foglamp-south-plugin$ python3 GitHub_Data_Generator/code/generate_github_data.py ~/auth_pair.txt localhost 6683 -s json -d /tmp

# Send to FogLAMP + Show Output 
~/foglamp-south-plugin$ python3 GitHub_Data_Generator/code/generate_github_data.py ~/auth_pair.txt localhost 6683 -s foglamp -d /tmp
~/foglamp-south-plugin$ curl -X GET http://localhost:8081/foglamp/asset | jq 
  {
    "count": 14,
    "assetCode": "github/FogLAMP/clones"
  },
  {
    "count": 30,
    "assetCode": "github/FogLAMP/commits/timestamp"
  },
  {
    "count": 1,
    "assetCode": "github/FogLAMP/commits/users"
  },
  {
    "count": 1,
    "assetCode": "github/FogLAMP/commits/users/Amarendra"
  },
  {
    "count": 1,
    "assetCode": "github/FogLAMP/commits/users/Ashwin-Gopalakrishnan"
  },
  {
    "count": 1,
    "assetCode": "github/FogLAMP/commits/users/Mark-Riddoch"
  },
  {
    "count": 1,
    "assetCode": "github/FogLAMP/commits/users/Praveen-Garg"
  },
  {
    "count": 1,
    "assetCode": "github/FogLAMP/commits/users/amarendra-dianomic"
  },
  {
    "count": 1,
    "assetCode": "github/FogLAMP/commits/users/ashwinscale"
  },
  {
    "count": 1,
    "assetCode": "github/FogLAMP/commits/users/pintomax"
  },
  {
    "count": 13,
    "assetCode": "github/FogLAMP/traffic"
  }


```

`System_Data` - The following utilizes `psutil` to get CPU, Memory, and Disk matrix regarding the FogLAMP env. 
```
# Help
~/foglamp-south-plugin$ python3 System_Data/code/generate_system_data.py --help
usage: generate_system_data.py [-h] [-s SEND] [-d DIR] host port

positional arguments:
  host                  FogLAMP POST Host
  port                  FogLAMP POST Port

optional arguments:
  -h, --help            show this help message and exit
  -s SEND, --send SEND  Where to send the data to (foglamp|json|both)
  -d DIR, --dir DIR     directory to send data into (for JSON)

# Send to JSON 
~/foglamp-south-plugin$ python3 System_Data/code/generate_system_data.py  localhost 6683 -s json -d /tmp

# Send to FogLAMP 
~/foglamp-south-plugin$ python3 System_Data/code/generate_system_data.py  localhost 6683 -s foglamp

# Sample JSON Output
~/foglamp-south-plugin$ cat /tmp/2018_07_26_15_13_08_system_stats.json | jq 
{
  "timestamp": "2018-07-26 15:13:08.219657",
  "key": "138532f2-9121-11e8-9313-0800275d93ce",
  "readings": {
    "cpu_0": 0,
    "iowait": 62.44,
    "system": 30.64,
    "idle": 10554.54
  },
  "asset": "system_cpu"
}
{
  "timestamp": "2018-07-26 15:13:08.219657",
  "key": "138532f3-9121-11e8-9313-0800275d93ce",
  "readings": {
    "warning": 0,
    "percent": 32
  },
  "asset": "system_memory"
}
{
  "timestamp": "2018-07-26 15:13:08.219657",
  "key": "138532f4-9121-11e8-9313-0800275d93ce",
  "readings": {
    "warning": 0,
    "useage": 29.9,
    "read": 18924,
    "write": 81756
  },
  "asset": "system_disk"
}
{
  "timestamp": "2018-07-26 15:13:08.219657",
  "key": "138532f5-9121-11e8-9313-0800275d93ce",
  "readings": {
    "percent": 100,
    "plugged": 1
  },
  "asset": "system_battery"
}
```

`Send_JSON` - Given a JSON file, send data into [FogLAMP]((https://github.com/foglamp/FogLAMP).
```
# Help
~/foglamp-south-plugin$ python3 Send_JSON/code/json_to_foglamp.py --help 
usage: json_to_foglamp.py [-h] file_name host port

positional arguments:
  file_name   File with JSON data
  host        FogLAMP POST Host
  port        FogLAMP POST Port

optional arguments:
  -h, --help  show this help message and exit 

# Send to FogLAMP + Show output 
~/foglamp-south-plugin$ python3 Send_JSON/code/json_to_foglamp.py /tmp/2018_07_26_15_13_08_system_stats.json 127.0.0.1 6683
~/foglamp-south-plugin$ curl -X GET http://localhost:8081/foglamp/asset | jq 
  {
    "count": 1,
    "assetCode": "system_battery"
  },
  {
    "count": 1,
    "assetCode": "system_cpu"
  },
  {
    "count": 1,
    "assetCode": "system_disk"
  },
  {
    "count": 1,
    "assetCode": "system_memory"
  }
```
