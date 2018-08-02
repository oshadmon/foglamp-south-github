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

   def prepare_foglamp(self):
      """
      Prepare FogLAMP env
      """
      os.system('bash $HOME/foglamp-south-plugin/FogLAMP/setup.sh')

   def start_foglamp(self): 
      """
      Start FogLAMP 
      """
      os.system('%s/scripts/foglamp start' % self.foglamp_dir) 
      stmt='{"name": "HTTP SOUTH", "type": "south", "plugin": "http_south", "enabled": true}'
      stmt="output=$(curl -sX POST http://localhost:8081/foglamp/service -d '%s')" % stmt
      print(stmt)
      os.system(stmt)

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
