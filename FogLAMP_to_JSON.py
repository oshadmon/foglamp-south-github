import datetime
import json 
import os 
import requests
import time 

class GetFogLAMPData: 
    def __init__(self, ip:str, prep_data_dir:str, send_data_dir:str): 
        """
        Init class 
        :args: 
           ip:str - IP that FogLAMP sits on 
           prep_data_dir:str - dir to prep data in 
           send_data_dir:str - dir location to store data
        :param: 
           self.asset_info:dict - asset information 
        """
        self.url = 'http://%s:8081/foglamp/asset' % ip
        self.prep_data_dir = self.__mkdir(prep_data_dir)
        self.send_data_dir = self.__mkdir(send_data_dir) 
        self.asset_info = {} 

    def __mkdir(self, dir_name:str)->str: 
        """
        Check if dir_name exists, if not create it 
        :args: 
           dir_name:str - dir to store data in 
        :return: 
           dir_name with full path
        """
        dir_name = os.path.expanduser(os.path.expandvars(dir_name))
        if os.path.isdir(dir_name) is False: 
            os.makedirs(dir_namme) 
        if '/' == dir_name[-1]: 
            dir_name = dir_name.rsplit("/", 1)[0]
        return dir_name

    def get_asset_info(self)->list: 
        """
        Using the base URL, get assets
        :return: 
           list of assets 
        """
        r = requests.get(self.url) 
        for asset in r.json(): 
            asset["assetCode"] = asset["assetCode"].replace("/", "%2F")
            if asset["assetCode"] not in  self.asset_info:
               self.asset_info[asset["assetCode"]] = asset["count"] 
            else: 
               self.asset_info[asset["assetCode"]] = asset["count"] - self.asset_info[asset["assetCode"]]
          
    def get_data(self)->dict: 
      """
      Using cURL get data from FogLAMP
      :return: 
         dict of data values 
      """ 
      assets_data = {}
      for asset in self.asset_info: 
         if self.asset_info[asset] > 0: 
            # sample URL: http://127.0.0.1:8081/foglamp/asset/asset_info?limit=X 
            # Currently we only get TIMESTAMP & values. Need to understand how to get all information 
            r = requests.get("%s/%s?limit=%s" % (self.url, asset, self.asset_info[asset]))
            assets_data[asset] = r.json() 
      return assets_data
   

    def __get_timestamp(self, asset_data:list)->str:
       """ 
       From data of a given asset get first timestamp, and convert it to a string of a numerical value
       :args: 
          asset_data:list - list of data points for a given data 
       :return: 
          Return first timestamp value as '%Y%m%d%H%M%S%f'
       """
       timestamps = []  
       if asset_data == {}: 
           return '' 
       for row in asset_data:
           timestamp = datetime.datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
           timestamp = timestamp.strftime('%Y%m%d%H%M%S%f')
           timestamps.append(timestamp)
       return str(sorted(timestamps)[0])

    def store_to_file(self, assets_data:dict):
       """
       Write data to file 
       :args: 
          assets_data:dict - dict of data to store in file(s) 
          timestammp_Asset_codes:dict - dict of start/end timestamps 
       """
       for asset in assets_data: 
           timestamp = self.__get_timestamp(assets_data[asset])
           file_name = self.prep_data_dir+"/%s.%s.json" % (timestamp, asset.replace("%2F", "_"))
           open(file_name, 'w').close()
           for row in assets_data[asset]:
               with open(file_name, 'a') as f: 
                   f.write("%s\n" % json.dumps(row))
           if self.send_data_dir != self.prep_data_dir:
               os.rename(file_name, file_name.replace(self.prep_data_dir, self.send_data_dir))

def main(): 
    ip = '192.168.7.215'
    send_data_dir = '/tmp'
    timestamp_assets_data = {} 

    gfd = GetFogLAMPData(ip, send_data_dir, send_data_dir)
    for i in range(2): 
       gfd.get_asset_info() 
       data = gfd.get_data()
       if data != {}: 
           gfd.store_to_file(data) 
       time.sleep(30)

if __name__ == '__main__': 
    main()
