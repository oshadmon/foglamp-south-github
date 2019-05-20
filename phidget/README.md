# Prerequisites
```
cd
sudo apt-get -y install build-essential
sudo apt-get install -y zip unzip
sudo apt-get install -y python3-setuptools
```
# Install 
* [System](https://www.phidgets.com/docs/OS_-_Linux#Quick_Downloads)
``` 
cd 
sudo apt-get install libusb-1.0-0-dev
wget https://www.phidgets.com/downloads/phidget22/libraries/linux/libphidget22.tar.gz 
tar -xzvf ~/libphidget22.tar.gz
cd ~/libphidget22-1.1.20190417  
sudo ./configure --prefix=/ && make && sudo make install
fn=`find -name *libphidget22.rule*`
sudo mv ${fn} /etc/udev/rules.d. 
``` 

* [Python](https://www.phidgets.com/docs/Language_-_Python) 
``` 
cd 
wget https://www.phidgets.com/downloads/phidget22/libraries/any/Phidget22Python.zip
unzip ~/Phidget22Python.zip
cd ~/Phidget22Python
sudo python3 setup.py install
```

# Supprted Module 
* Humidity and Temperature [HUM1000_0](https://www.phidgets.com/?tier=3&catid=14&pcid=12&prodid=644)
* Current [VCP1001_0](https://www.phidgets.com/?tier=3&catid=16&pcid=14&prodid=954)
* Spatial Phidget [MOT1101_0](https://www.phidgets.com/?tier=3&catid=10&pcid=8&prodid=975)
* Encoder 



