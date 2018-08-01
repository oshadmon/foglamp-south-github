# Prerequisites
cd $HOME
sudo apt-get install avahi-daemon curl git cmake g++ make build-essential autoconf automake
sudo apt-get install sqlite3 libsqlite3-dev
sudo apt-get install libtool libboost-dev libboost-system-dev libboost-thread-dev libssl-dev libpq-dev uuid-dev
sudo apt-get install python3-dev python3-pip python3-dbus python3-setuptools
sudo apt-get install postgresql

# Clone FogLAMP
cd $HOME
git clone https://github.com/foglamp/FogLAMP.git 

# Setup FogLAMP
cd FogLAMP 
git checkout master 
make 


# HTTP connection 
cd $HOME
git clone https://github.com/foglamp/foglamp-south-http.git
cp $HOME/foglamp-south-http/python $HOME/FogLAMP/

