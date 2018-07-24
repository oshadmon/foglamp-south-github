"""
Name: Ori Shadmon
Date: July 2018
Description: Retrieve system insight and store it into JSON file 
""" 
import aiohttp
import argparse
import asyncio
import datetime 
import json
import os
import platform
import psutil
import queue
import sys
import time 
import threading
import uuid

# Process to import files from FogLAMP repo
# Requires FogLAMP to be downloaded into $HOME (git clone https://github.com/foglamp/FogLAMP.git) 
env=os.path.expanduser(os.path.expandvars('$HOME/FogLAMP'))
sys.path.insert(0, env)
from python.foglamp.services.south import exceptions

def get_timestamp(que:queue.Queue=None)->str: 
   """
   :return: 
      Current timestamp as string 
   """
   que.put(datetime.datetime.now())

def cpu_insight(que:queue.Queue=None)->dict: 
   """ 
   Get CPU utilization insight 
   :return: 
      dict with CPU info - precentage (per CPU), system, idle, and iowait 
   """
   # Precetnage utilized per CPU
   precentage=psutil.cpu_percent(interval=None, percpu=True) 
   precentage_data={}
   for i in range(len(precentage)):
      precentage_data['cpu_%s' % i]=precentage[i]

   # CPU times 
   output=psutil.cpu_times()
   system=output[2]
   idle=output[3]
   iowait=output[4]
   
   # Store all generated data into a single dict 
   cpu_data={} 
   for key in precentage_data: 
      cpu_data[key]=precentage_data[key] 
   cpu_data['system']=system
   cpu_data['idle']=idle
   cpu_data['iowait']=iowait
   que.put(cpu_data)
   
def mem_insight(que:queue.Queue=None)->dict: 
   """
   Get Memory utilization insight
   :return: 
      dict with Memory info - precentage and whether or not it's at risk 
   """
   mem=psutil.virtual_memory()
   percent=mem.percent
   warning=0 
   if percent > 90: 
      warning=1 
   que.put({'percent': percent, 'warning': warning})

def disk_insight(que:queue.Queue=None)->dict:
   """
   Get Disk utilization insight
   :return: 
      dict with Disk info - useage, I/O
   """ 
   useage=psutil.disk_usage('/')[3] 
   warning=0
   if useage > 75.55: #warning enabled when disk utilizes more than 75% of data
      warning=1
   output=psutil.disk_io_counters() 
   read_count=output.read_count 
   write_count=output.write_count

   que.put({'useage': useage, 'warning': warning, 'read': read_count, 'write': write_count}) 

def battery_precent(que:queue.Queue=None)->dict: 
   """
   Get Battery precent and status
   :return: 
      dict with battery info - precent, and whether plugged-in
   """
   battery = psutil.sensors_battery()
   plugged = battery.power_plugged
   if plugged is True: 
      plugged=1
   else: 
      plugged=0
   percent = battery.percent
   que.put({'precent': percent, 'plugged': plugged})

def get_data()->(str, dict, dict, dict, dict): 
   """
   In parallel get insight regarding machine
   :return: 
      Data generated from insight 
   """
   timestamp_que=queue.Queue()
   cpu_que=queue.Queue()
   mem_que=queue.Queue() 
   disk_que=queue.Queue()
   battery=queue.Queue()

   threads=[threading.Thread(target=get_timestamp,    args=(timestamp_que,)), 
            threading.Thread(target=cpu_insight,      args=(cpu_que,)), 
            threading.Thread(target=mem_insight,      args=(mem_que,)),
            threading.Thread(target=disk_insight,     args=(disk_que,)),
            threading.Thread(target=battery_precent,  args=(battery,))
           ]

   for thread in threads: 
      thread.start() 
   for thread in threads: 
      thread.join()
   timestamp=timestamp_que.get() 
   cpu_data=cpu_que.get() 
   mem_data=mem_que.get() 
   disk_data=disk_que.get() 
   battery_data=battery.get()
   return timestamp, cpu_data, mem_data, disk_data, battery_data

def create_json(timestamp:datetime.datetime=datetime.datetime.now(), data:dict={}, asset:str='cpu')->dict:
   """
   Generate JSON from info 
   :args: 
      timestamp:datetime.datetime - time data was generated 
      data:dict - dictionary with data for a given asset 
      asset:dict - info provided 
   :return: 
      JSON object (as dict) to store in file
   """
   return {'timestamp': str(timestamp), 
           'key':       str(uuid.uuid1()), 
           'asset':    'system_%s' % asset, 
           'readings':   data
          }

def write_to_file(env:str='/tmp', timestamp:datetime.datetime=datetime.datetime.now(), cpu_data:str={"":""}, 
                  mem_data:str={"":""}, disk_data:str={"":""}, battery_data:str={"":""}): 
   """
   Write JSON data into /tmp/system_data.json 
   :args:
      env:str - directory storing data in 
      timestamp:datetime.datetime - time data was generated 
      cpu_data:str - JSON object with CPU insight 
      mem_data:str - JSON object with memory insight 
      disk_data:str - JSON object with disk insight
      battery_data:str - JSON object with battery insight
   """
   file_name=env+'/system_data_%s.json' % timestamp.strftime('%Y_%m_%d_%H_%M_%S')
   open(file_name, 'w').close()
   f=open(file_name, 'w') 
   f.write(cpu_data)
   f.write(mem_data)
   f.write(disk_data)
   f.write(battery_data)
   f.close()

async def send_to_foglamp(payload:dict={}, arg_host:str='localhost', arg_port:int=6683):
    """
    POST request to:
     localhost
     port 5683 (official IANA assigned CoAP port),
     URI "/other/sensor-values".
    """
    headers = {'content-type': 'application/json'}
    url = 'http://{}:{}/sensor-reading'.format(arg_host, arg_port)
    async with aiohttp.ClientSession() as session:
       async with session.post(url, data=json.dumps(payload), headers=headers) as resp:
          print(resp.text())
          await resp.text()
          status_code = resp.status
          print(status_code) 
          if status_code in range(400, 500):
             print("Bad request error | code:{}, reason: {}".format(status_code, resp.reason))
             return False
          if status_code in range(500, 600):
             print("Server error | code:{}, reason: {}".format(status_code, resp.reason))
             return False
          return True

    
def main(): 
   parser = argparse.ArgumentParser()
   parser.add_argument('host', default='localhost', help='FogLAMP POST Host') 
   parser.add_argument('port', default=6683, help='FogLAMP POST Port')
   args = parser.parse_args()

   loop = asyncio.get_event_loop()
   timestamp, cpu_data, mem_data, disk_data, battery_data=get_data() 

   cpu_data=create_json(timestamp, cpu_data, 'cpu') 
   loop.run_until_complete(send_to_foglamp(cpu_data))
   #mem_data=create_json(timestamp, mem_data, 'memory')
   #disk_data=create_json(timestamp, disk_data, 'disk')
   #battery_data=create_json(timestamp, battery_data, 'battery')

   #write_to_file(env, timestamp, cpu_data, mem_data, disk_data, battery_data)
   

if __name__ == '__main__': 
   main() 
