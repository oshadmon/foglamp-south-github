# foglamp-south-github
The following scripts take data from different components (such as _GitHub_ and _Google Analytics_), and send it into [FogLAMP](https://github.com/foglamp/FogLAMP).  


# What is FogLAMP:
[FogLAMP](https://github.com/foglamp/FogLAMP) is an open source platform for the **Internet of Things**, and an essential component in **Fog Computing**. It uses a modular **microservices architecture** including sensor data collection, storage, processing and forwarding to historians, Enterprise systems and Cloud-based services. FogLAMP can run in highly available, stand alone, unattended environments that assume unreliable network connectivity.
.

# Files
`GitHub_Data_Generator` - The following is based on [github-traffic-stats](https://github.com/nchah/github-traffic-stats), retrieving data from GitHub and send it to FogLAMP. 

`System_Data` - The following utilizes `psutil` to get CPU, Memory, and Disk matrix regarding the FogLAMP env. 
