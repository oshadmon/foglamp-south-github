"""
Name: Ori Shadmon
Date: June/July 2018
Description: Send JSON data into FogLAMP 
The code utilizes ideas from fogbench (https://github.com/foglamp/FogLAMP/blob/develop/extras/python/fogbench/__main__.py) 
""" 
import sys
import os
import random
import json
from datetime import datetime, timezone
import argparse
import uuid
import collections

import asyncio
import aiohttp
from aiocoap import *
from cbor2 import dumps

def send_to_foglamp(payload:dict={}): 
   """
   Send data into foglamp
   :args:
      payload:dict - data to sent to foglamp
   """
   context =  Context.create_client_context()
   request = Message(payload=dumps(payload), code=POST)
   request.opt.uri_host = 'localhost'
   request.opt.uri_port = 6683
   request.opt.uri_path = ("other", "sensor-values")
   response = context.request(request).response

   

def read_data(file_name:str='/tmp/data.json', keep:bool=True)->list: 
   """
   Get data from file 
   :args:
      file_name:str - file containing
      keep:bool - Keep JSON file (default True) 
   :return: 
      list with data from file_name as a dictionary
   """
   data=[]
   with open(file_name, 'r') as f: 
      for line in f.readlines(): 
         data.append(json.loads(line))
   if keep is False: 
      os.system("rm -rf %s" % file_name)
   return data 

def main(): 
   parser = argparse.ArgumentParser()
   parser.add_argument('file_name', default='/tmp/data.json', type=str, help='File with JSON data')
   parser.add_argument('keep', default=True, type=bool, help='Whether or not to keep JSON file') 
   args = parser.parse_args() 
   data=read_data(args.file_name, args.keep)
   loop = asyncio.get_event_loop()
   for payload in data: 
      send_to_foglamp(payload)

if __name__ == '__main__': 
   main()
