import argparse 
import os 

class FogLAMP: 
   def __init__(self, foglamp_dir:str='$HOME/FogLAMP', foglamp_south_http:str='$HOME/foglamp-south-http'): 
      """
      FogLAMP related calls 
      :param:
         foglamp_dir:str - dir with clone of FogLAMP (https://github.com/foglamp/FogLAMP) 
         foglamp_sout_http:str - dir with clone of FogLAMP South HTTP plugin (https://github.com/foglamp/foglamp-south-http)
      """
      self.foglamp_dir        = os.path.expanduser(os.path.expandvars(foglamp_dir))
      self.foglamp_south_http = os.path.expanduser(os.path.expandvars(foglamp_south_http))

      self.__get_latest()  
      os.system('export FogLAMP_ROOT=%s' % self.foglamp_dir)

   def __get_latest(self): 
      """
      Get latest code 
      Errors might occur if the user does any changes in either dir without doing add/commit before executing
      """	
      os.system('cd %s; git checkout develop;  git pull origin develop' % self.foglamp_dir)
      os.system('cd %s; git checkout master;  git pull origin master' % self.foglamp_south_http)
      os.system('cd $HOME')

   def prepare_foglamp(self):
      """
      Prepare FogLAMP env
      """
      os.system('bash %s/FogLAMP/setup.sh' % self.foglamp_south_http)

   def __start_http(self):
      """
      Start http service
      """
      os.system('cp -r %s/python %s' % (self.foglamp_south_http, self.foglamp_dir))
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
   """
   Script to execute start/stop/reset for FogLAMP
   :positional arguments:
      call                  process to call (prepare | start | stop | reset | status)
   :optional arguments:
      -h, --help                                    show this help message and exit
      -f, --foglamp                                 cloned FogLAMP directory path
      -sh --foglamp-south-http FOGLAMP_SOUTH_HTTP   cloned FogLAMP South HTTP path
   """
   parser = argparse.ArgumentParser() 
   parser.add_argument('call',            default='status',                   type=str, help='process to call (prepare | start | stop | reset | status)') 
   parser.add_argument('-f', '--foglamp', default='$HOME/FogLAMP',            type=str, help='cloned FogLAMP directory path') 
   parser.add_argument('-sh', '--foglamp-south-http',    default='$HOME/foglamp_south_http', type=str, help='cloned FogLAMP South HTTP path')
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
