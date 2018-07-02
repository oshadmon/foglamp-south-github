# Description
Based on [github-traffic-stats](https://github.com/nchah/github-traffic-stats), the script inserts GitHub data into [FogLAMP](https://github.com/foglamp/FogLAMP). 

# Files
`code/generate_json_files.py` - Script to generate data from GitHub 
`code/test_generate_json_files.py` - pytest for generate_json_files.py
`other/auth_pair.txt' - Authentication pair file should contain GitHub access and repo/org you want to run against
`sample/*.json` - Sample JSON files for the different GitHub params

# Example 
```
# Generate JSON data 
-- Help
ubuntu@ubuntu:~/foglamp-south-github$ python3 code/generate_json_files.py --help
positional arguments:
   auth_file   authentication file
-- Execute 
ubuntu@ubuntu:~/foglamp-south-github$ python3 GitHub_Data_Generator/code/generate_json_files.py $HOME/foglamp-south-plugin/GitHub_Data_Generator/other/auth_pair.txt
-- Pytest (Need to sample/auth_pair.txt prior to running) 
ubuntu@ubuntu:~/foglamp-south-github$ pytest GitHub_Data_Generator/code/test_generate_json_files.py 
``` 
