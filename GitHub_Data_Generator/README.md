# Description
Based on [github-traffic-stats](https://github.com/nchah/github-traffic-stats), the script inserts GitHub data into [FogLAMP](https://github.com/foglamp/FogLAMP). 

# Files
`code/generate_json_files.py` - Script to generate data from GitHub 
`code/test_generate_json_files.py` - pytest for generate_json_files.py
`sample/auth_pair.txt' - Authentication pair file (should be in $HOME in order to run pytest)
`sample/*.json` - Sample JSON files for the different GitHub params

# Example 
```
# Generate JSON data 
-- Help
ubuntu@ubuntu:~/foglamp-south-github$ python3 code/generate_json_files.py --help
positional arguments:
  username              Github username
  repo                  User's repo

optional arguments:
  -h, --help                       show this help message and exit
  -o ORGANIZATION, --organization  Github organization

-- Execute 
ubuntu@ubuntu:~/foglamp-south-github$ python3 GitHub_Data_Generator/code/generate_json_files.py user@github.com:password FogLAMP foglamp
-- Pytest (Need to sample/auth_pair.txt prior to running) 
ubuntu@ubuntu:~/foglamp-south-github$ pytest GitHub_Data_Generator/code/test_generate_json_files.py 
``` 
