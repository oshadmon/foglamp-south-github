#!/bin/bash
if [ $# -ne 1 ];then
 echo "usage: authentication file"
 exit 1
fi

auth_file=$1

# Generate GitHub data and send it to JSON files
python3 $HOME/foglamp-south-plugin/GitHub_Data_Generator/code/generate_json_files.py ${auth_file}
python3 $HOME/foglamp-south-plugin/System_Data/code/generate_system_data.py


