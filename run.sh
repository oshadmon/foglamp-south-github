#!/bin/bash
if [ $# -ne 3 ];then
 echo "usage: user:password organization repo"
 exit 1
fi

user=$1
org=$2 
repo=$3

# Generate GitHub data and send it to JSON files
python3 $HOME/foglamp-south-plugin/GitHub_Data_Generator/code/generate_json_files.py ${user} ${repo} -o ${org} 


