# Prerequisites
cd $HOME
sudo apt-get install avahi-daemon curl git cmake g++ make build-essential autoconf automake
sudo apt-get install sqlite3 libsqlite3-dev
sudo apt-get install libtool libboost-dev libboost-system-dev libboost-thread-dev libssl-dev libpq-dev uuid-dev
sudo apt-get install python3-dev python3-pip python3-dbus python3-setuptools
sudo apt-get install postgresql

# Clone FogLAMP
git clone https://github.com/foglamp/FogLAMP.git 

# Setup FogLAMP
cd FogLAMP 
make 

# Start FogLAMP 
export FOGLAMP_ROOT=$HOME/FogLAMP
scripts/foglamp start 
scripts/foglamp status

# HTTP connection 
cd $HOME
git clone https://github.com/foglamp/foglamp-south-http.git
cp $HOME/foglamp-south-http/python $HOME/FogLAMP/

# Sart HTTP Connection 
output=$(curl -sX POST http://localhost:8081/foglamp/service -d '{"name": "HTTP SOUTH", "type": "south", "plugin": "http_south", "enabled": true}')


# Remove HTTP clone 
rm -rf $HOME/foglamp-south-http/python

