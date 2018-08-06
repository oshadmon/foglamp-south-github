import argparse 
import os 
class FogLAMP: 
   def __init__(self): 
      """
      FogLAMP related calls 
      """
      self.foglamp_dir=os.path.expanduser(os.path.expandvars('$HOME/FogLAMP'))
      if os.path.isdir(self.foglamp_dir) is True: 
         os.environ['FOGLAMP_ROOT']=self.foglamp_dir 
      self.__get_latest()  


   def __get_latest(self): 
      """
      Get latest code 
      """
      os.system('cd $HOME/FogLAMP; git checkout develop;  git pull origin develop')
      os.system('cd $HOME/foglamp-south-http; git checkout master; git pull origin master')
      os.system('cd $HOME')

   def prepare_foglamp(self):
      """
      Prepare FogLAMP env
      """
      os.system('bash $HOME/foglamp-south-plugin/FogLAMP/setup.sh')

   def __start_http(self):
      """
      Start http service
      """
      os.system('cp -r $HOME/foglamp-south-http/python ~/FogLAMP')
      stmt='{"name": "HTTP SOUTH", "type": "south", "plugin": "http_south", "enabled": true}'
      stmt="output=$(curl -sX POST http://localhost:8081/foglamp/service -d '%s')" % stmt
      os.system(stmt)

   def start_foglamp(self): 
      """
      Start FogLAMP 
      """
      os.system('%s/scripts/foglamp start' % self.foglamp_dir) 
      self.__start_http() 

   def stop_foglamp(self):
      """
      Stop FogLAMP 
      """
      os.system('%s/scripts/foglamp stop' % self.foglamp_dir)

   def reset_foglamp(self): 
      """
      Restart FogLAMP
      """
      os.system('%s/scripts/foglamp reset' % self.foglamp_dir)

   def status_foglamp(self): 
      """
      FogLAMP status 
      """
      os.system('%s/scripts/foglamp status' % self.foglamp_dir) 

def main(): 
   parser = argparse.ArgumentParser() 
   parser.add_argument('call', default='status', type=str, help='process to call (prepare | start | stop | reset | status)') 
   args = parser.parse_args()

   foglamp=FogLAMP() 
   if args.call.lower() == 'prepare': 
      foglamp.prepare_folamp() 
   elif args.call.lower() == 'start': 
      foglamp.start_foglamp()
   elif args.call.lower() == 'stop': 
      foglamp.stop_foglamp()
   elif args.call.lower() == 'reset': 
      foglamp.reset_foglamp()
   else: # In all other cases show status 
      foglamp.status_foglamp()

if __name__ == '__main__': 
   main()
