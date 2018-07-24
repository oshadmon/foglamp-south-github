"""
Name: Ori Shadmon
Date: July 2018
Description: Retrieve system insight and store it into JSON file 
""" 
import argparse
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
def write_to_file(file_name:str='/tmp/data.json', data:dict={}):
   """
   Write to File 
   :args: 
      file_name:str - File containing data 
      data:dict - Dictionary with data
   """
   with open(file_name, 'a') as f: 
      #f.write('\n')
      f.write(json.dumps(data)) 

def main(): 
   """
   Main for generating GitHub data and sending it to FogLAMP 
   :param: 
      dir:str - Directory to store results
   """
   parser = argparse.ArgumentParser()
   parser.add_argument('dir', default='/tmp', help='Directory to store results') 
   args = parser.parse_args()
 
   # Raw data 
   timestamp, cpu_data, mem_data, disk_data, battery_data=get_data() 

   # Prepare data 
   cpu_data=create_json(timestamp, cpu_data, 'cpu') 
   mem_data=create_json(timestamp, mem_data, 'memory')
   disk_data=create_json(timestamp, disk_data, 'disk')
   battery_data=create_json(timestamp, battery_data, 'battery')

   # Write to file  
   file_name=args.dir+'/%s_system_stats.json' % datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') 
   open(file_name, 'w').close() 
   write_to_file(file_name, cpu_data)
   write_to_file(file_name, mem_data)
   write_to_file(file_name, disk_data)
   write_to_file(file_name, battery_data)
   

if __name__ == '__main__': 
   main() 
