# foglamp-south-github
Based on [github-traffic-stats](https://github.com/nchah/github-traffic-stats), the script inserts GitHub data into [FogLAMP](https://github.com/foglamp/FogLAMP). 


# FogLAMP Description
FogLAMP is an open source platform for the **Internet of Things**, and an essential component in **Fog Computing**. It uses a modular **microservices architecture** including sensor data collection, storage, processing and forwarding to historians, Enterprise systems and Cloud-based services. FogLAMP can run in highly available, stand alone, unattended environments that assume unreliable network connectivity.
.

# Files
`code/generate_json_files.py` - Script to generate data from GitHub 
`code/test_generate_json_files.py` - pytest for generate_json_files.py
`sample/auth_pair.txt' - Authentication pair file (should be in $HOME in order to run pytest)
`sample/*.json` - Sample JSON files for the different GitHub params

# Example 
```
-- Help
ubuntu@ubuntu:~/foglamp-south-github$ python3 code/generate_json_files.py --help
positional arguments:
  username              Github username
  repo                  User's repo

optional arguments:
  -h, --help                       show this help message and exit
  -o ORGANIZATION, --organization  Github organization

-- Execute 
ubuntu@ubuntu:~/foglamp-south-github$ python3 code/generate_json_files.py user@github.com:password FogLAMP foglamp
``` 
