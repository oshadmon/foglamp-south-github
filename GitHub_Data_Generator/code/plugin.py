"""
Name: Ori Shadmon
Date: June/July 2018
Description: Send JSON data into FogLAMP 
The code utilizes ideas from fogbench (https://github.com/foglamp/FogLAMP/blob/develop/extras/python/fogbench/__main__.py) 
""" 
import argparse
import json


def read_data(file_name:str='/tmp/data.json')->list: 
   """
   Get data from file 
   :args:
      file_name:str - file containing
   :return: 
      list with data from file_name as a dictionary
   """
   data=[]
   with open(file_name, 'r') as f: 
      for line in f.readlines(): 
         data.append(json.loads(line))
   return data 

def main(): 
   parser = argparse.ArgumentParser()
   parser.add_argument('file_name', default='/tmp/data.json', type=str, help='File with JSON data')
   args = parser.parse_args() 
   data=read_data(args.file_name)


if __name__ == '__main__': 
   main()
