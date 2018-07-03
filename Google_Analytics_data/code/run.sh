if [ $# -ne 1 ] 
then 
   echo "missing $HOME/client_secrets.json file" 
fi 
client_secrets=$1

# Set both authentication script and client_secrets.json to be in /tmp dir
dir_name="$HOME/ga_$(date +'%Y_%m_%d_%H_%M')" 
mkdir ${dir_name}
cp $HOME/foglamp-south-plugin/Google_Analytics_data/code/authenticate_google.py ${dir_name} 
echo ${client_secrets}
cp -r ${client_secrets} ${dir_name}

python3 ${dir_name}/authenticate_google.py --noauth_local_webserver

rm -rf ${dir_name} 
