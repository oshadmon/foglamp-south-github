"""
Name: Ori Shadmon
Date: July 2018
Description: The following takes JSON data and sends it into FogLAMP 
"""
import aiohttp
import argparse
import asyncio
import json

def file_to_list(file_name:str='/tmp/data.json')->list: 
   """
   Convert data in file into a list of JSON objects 
   :args: 
      file_name:str - File containing JSON 
   :return: 
      list of JSON objects from file 
   """ 
   data=[]
   with open(file_name) as f:
      for line in f:
         data.append(line)
   return data 

async def send_to_foglamp(payload:dict={}, arg_host:str='localhost', arg_port:int=6683):
    """
    POST to FogLAMP using HTTP 
    :args: 
       payload:dict - Dictionary with data 
       arg_host:str - FogLAMP Host 
       arg_port:int - FogLAMP POST port 
    """
    headers = {'content-type': 'application/json'}
    url = 'http://{}:{}/sensor-reading'.format(arg_host, arg_port)
    async with aiohttp.ClientSession() as session:
       async with session.post(url, data=payload, headers=headers) as resp:
          await resp.text()
          status_code = resp.status
          if status_code in range(400, 500):
             return "Bad request error | code:{}, reason: {}".format(status_code, resp.reason)
          if status_code in range(500, 600):
             return "Server error | code:{}, reason: {}".format(status_code, resp.reason)
          return 0

def main(): 
   """
   Given a JSON file, write results to FogLAMP
   :param; 
      file_name:str - File containing JSON object(s)
      host:str - FogLAMP POST host
      port:int - FogLAMP POST port

   :sample JSON file - System_Data/sample/2018_07_24_13_21_33_system_stats.json: 
      {"key": "28908ea6-8f7f-11e8-9a8f-0800275d93ce", "readings": {"cpu_0": 100.0, "idle": 9681.3, "iowait": 148.55, "system": 53.64}, "asset": "system_cpu", "timestamp": "2018-07-24 13:21:33.893927"}
      {"key": "28908ea7-8f7f-11e8-9a8f-0800275d93ce", "readings": {"percent": 35.2, "warning": 0}, "asset": "system_memory", "timestamp": "2018-07-24 13:21:33.893927"}
      {"key": "28908ea8-8f7f-11e8-9a8f-0800275d93ce", "readings": {"warning": 0, "useage": 30.0, "write": 599646, "read": 18618}, "asset": "system_disk", "timestamp": "2018-07-24 13:21:33.893927"}
      {"key": "28908ea9-8f7f-11e8-9a8f-0800275d93ce", "readings": {"plugged": 0, "precent": 82.0}, "asset": "system_battery", "timestamp": "2018-07-24 13:21:33.893927"}
   """
   parser = argparse.ArgumentParser()
   parser.add_argument('file_name', default='/tmp/data.json', help='File with JSON data')
   parser.add_argument('host', default='localhost', help='FogLAMP POST Host')
   parser.add_argument('port', default=6683, help='FogLAMP POST Port')
   args = parser.parse_args()

   # get data from file 
   data=file_to_list(args.file_name)

   # Send to FogLAMP - if error occurs stop  
   loop = asyncio.get_event_loop()
   for obj in data: 
      output=loop.run_until_complete(send_to_foglamp(obj, args.host, args.port))
      if output != 0: 
         print(output) 
         exit(1)
 
if __name__ == '__main__': 
   main()
