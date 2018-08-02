"""
Name: Ori Shadmon
Date: July 2018
Description: Retrieve system insight and send it into FogLAMP 
""" 
import aiohttp
import argparse
import asyncio
import datetime 
import json
import psutil
import queue
import time 
import threading
import uuid

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
      dict with CPU info - percentage (per CPU), system, idle, and iowait 
   """
   # Precetnage utilized per CPU
   percentage=psutil.cpu_percent(interval=None, percpu=True) 
   percentage_data={}
   for i in range(len(percentage)):
      percentage_data['cpu_%s' % i]=percentage[i]

   # CPU times 
   output=psutil.cpu_times()
   system=output[2]
   idle=output[3]
   iowait=output[4]
   
   # Store all generated data into a single dict 
   cpu_data={} 
   for key in percentage_data: 
      cpu_data[key]=percentage_data[key] 
   cpu_data['system']=system
   cpu_data['idle']=idle
   cpu_data['iowait']=iowait
   que.put(cpu_data)
   
def mem_insight(que:queue.Queue=None)->dict: 
   """
   Get Memory utilization insight
   :return: 
      dict with Memory info - percentage and whether or not it's at risk 
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

   threads=[threading.Thread(target=get_timestamp,    args=(timestamp_que,)), 
            threading.Thread(target=cpu_insight,      args=(cpu_que,)), 
            threading.Thread(target=mem_insight,      args=(mem_que,)),
            threading.Thread(target=disk_insight,     args=(disk_que,)),
           ]

   for thread in threads: 
      thread.start() 
   for thread in threads: 
      thread.join()
   timestamp=timestamp_que.get() 
   cpu_data=cpu_que.get() 
   mem_data=mem_que.get() 
   disk_data=disk_que.get() 
   return timestamp, cpu_data, mem_data, disk_data

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

async def send_to_foglamp(payload, arg_host:str='localhost', arg_port:int=6683):
    """
    POST to FogLAMP using HTTP 
    :args: 

       arg_port:int - FogLAMP POST port 
    """
    headers = {'content-type': 'application/json'}
    url = 'http://{}:{}/sensor-reading'.format(arg_host, arg_port)
    async with aiohttp.ClientSession() as session:
       async with session.post(url, data=json.dumps(payload), headers=headers) as resp:
          await resp.text()
          status_code = resp.status
          if status_code in range(400, 500):
             print("Bad request error | code:{}, reason: {}".format(status_code, resp.reason))
             exit(1)
          if status_code in range(500, 600):
             print("Server error | code:{}, reason: {}".format(status_code, resp.reason))
             exit(1)

def write_to_file(file_name:str='/tmp/data.json', data:dict={}):
   """
   Write to File 
   :args: 
      file_name:str - File containing data 
      data:dict - Dictionary with data
   """
   with open(file_name, 'a') as f:
      f.write(json.dumps(data))
      f.write('\n')

def main(): 
   """
   Main for generating GitHub data and sending it to FogLAMP 
   :positional arguments:
      host                  FogLAMP POST Host
      port                  FogLAMP POST Port

   :optional arguments:
      -h, --help            show this help message and exit
      -s SEND, --send SEND  Where to send the data to (foglamp|json|both)
      -d DIR, --dir DIR     directory to send data into (for JSON)
   """
   parser = argparse.ArgumentParser()
   parser.add_argument('host', default='localhost', help='FogLAMP POST Host') 
   parser.add_argument('port', default=6683, help='FogLAMP POST Port')
   parser.add_argument('-s', '--send', default='foglamp', help='Where to send the data to (foglamp|json|both)')
   parser.add_argument('-d', '--dir', default='/tmp', help='directory to send data into (for JSON)')
   args = parser.parse_args()

   # Raw data 
   timestamp, cpu_data, mem_data, disk_data=get_data() 
  
   # Prepare Data  
   cpu_data=create_json(timestamp, cpu_data, 'cpu') 
   mem_data=create_json(timestamp, mem_data, 'memory')
   disk_data=create_json(timestamp, disk_data, 'disk')
   
   loop = asyncio.get_event_loop()
   file_name=args.dir+'/%s_system_stats.json' % datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
   if args.send.lower() == 'foglamp': # Send to FogLAMP
      loop.run_until_complete(send_to_foglamp(cpu_data, args.host, args.port))
      loop.run_until_complete(send_to_foglamp(mem_data, args.host, args.port))
      loop.run_until_complete(send_to_foglamp(disk_data, args.host, args.port))
   elif args.send.lower() == 'json': # Send to JSON 
      write_to_file(file_name, cpu_data)
      write_to_file(file_name, mem_data)
      write_to_file(file_name, disk_data)
   else: # If not FogLAMP or JSON then send to both
      loop.run_until_complete(send_to_foglamp(cpu_data, args.host, args.port))
      loop.run_until_complete(send_to_foglamp(mem_data, args.host, args.port))
      loop.run_until_complete(send_to_foglamp(disk_data, args.host, args.port))
      write_to_file(file_name, cpu_data)
      write_to_file(file_name, mem_data)
      write_to_file(file_name, disk_data)

if __name__ == '__main__': 
   main() 
