"""
Name: Ori Shadmon
Date: July 2018
Description: Retrieve system insight and store it into JSON file 
""" 
import argparse
import datetime 
import json
import os
import platform
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
   warning=False 
   if percent > 90: 
      warning=True 
   que.put({'percent': percent, 'warning': warning})

def disk_insight(que:queue.Queue=None)->dict:
   """
   Get Disk utilization insight
   :return: 
      dict with Disk info - useage, I/O
   """ 
   useage=psutil.disk_usage('/')[3] 
   warning=False
   if useage > 75.55: #warning enabled when disk utilizes more than 75% of data
      warning=True 
   output=psutil.disk_io_counters() 
   read_count=output.read_count 
   write_count=output.write_count

   que.put({'useage': useage, 'warning': warning, 'read': read_count, 'write': write_count}) 

def get_data()->(str, dict, dict, dict): 
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
            threading.Thread(target=disk_insight,     args=(disk_que,))
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

def create_json(timestamp:datetime.datetime=datetime.datetime.now(), data:dict={}, asset:str='cpu')->str:
   """
   Generate JSON from info 
   :args: 
      timestamp:datetime.datetime - time data was generated 
      data:dict - dictionary with data for a given asset 
      asset:dict - info provided 
   :return: 
      JSON object to store in file
   """
   json_data=json.dumps({'timestamp': str(timestamp), 
                         'key':       str(uuid.uuid1()), 
                         'asset':     'system/%s' % asset, 
                         'readings':   data
                       })
   return json_data

def write_to_file(env:str='/tmp', timestamp:datetime.datetime=datetime.datetime.now(), cpu_data:str={"":""}, mem_data:str={"":""}, disk_data:str={"":""}): 
   """
   Write JSON data into /tmp/system_data.json 
   :args:
      env:str - directory storing data in 
      timestamp:datetime.datetime - time data was generated 
      cpu_data:str - JSON object with CPU insight 
      mem_data:str - JSON object with memory insight 
      disk_data:str - JSON object with disk insight
   """
   file_name=env+'/system_data_%s.json' % timestamp.strftime('%Y_%m_%d_%H_%M_%S')
   open(file_name, 'w').close()
   f=open(file_name, 'w') 
   f.write(cpu_data)
   f.write(mem_data)
   f.write(disk_data)
   f.close()

def main(): 
   parser = argparse.ArgumentParser()
   parser.add_argument('data_dir', default='/tmp', help='dir to store results')
   args = parser.parse_args()
   env=os.path.expanduser(os.path.expandvars(args.data_dir)) 

   timestamp, cpu_data, mem_data, disk_data=get_data() 
   cpu_data=create_json(timestamp, cpu_data, 'cpu') 
   mem_data=create_json(timestamp, mem_data, 'memory')
   disk_data=create_json(timestamp, disk_data, 'disk')

   write_to_file(env, timestamp, cpu_data, mem_data, disk_data)

if __name__ == '__main__': 
   main() 
