# Description
The following retrieves data from Google Analytics, and storing it in JSON file(s).

Code is incomplete

# Files 
- `code/authenticate_google.py` - Authenticate connection to Google Analytics. Code is originally from [google-api-python-client/hello_analytics_api_v3.py](https://github.com/google/google-api-python-client/blob/master/samples/analytics/hello_analytics_api_v3.py)

- `code/run.sh` - Copy `code/authenticate_google.py` and `client_secrets.json` to a single location, then run `client_secrets.json` 

- `/tmp/client_secrets.json` - JSON file with API connection info. File needs to be created / downloaded from [Google API Console](https://console.developers.google.com/)

# Requirements 
- Install [Google API Python Client](https://github.com/google/google-api-python-client) - `pip install --upgrade google-api-python-client`

- In [Google API Console](https://console.developers.google.com/) do the following
   1) Enable [Google Analytics](https://console.developers.google.com/apis/library/analyticsreporting.googleapis.com?q=Google%20Analytics&id=a6268697-60ed-41f3-afb3-5305fbcced6b&project=steel-math-209022)) 
   2) In [Credentials](https://console.developers.google.com/apis/credentials) create a OAuth 2.0 credential 

- Download credentials 

# Run
```
-- Running code/authenticate_google.py (verify client_secrets.json is in the same dir)
ubuntu@ubuntu:~/foglamp-south-plugin$ python3 Google_Analytics_data/code/authenticate_google.py ^C
-- Run when files aren't in the same dir 
ubuntu@ubuntu:~/foglamp-south-plugin$ bash Google_Analytics_data/code/run.sh $HOME/foglamp-south-plugin/Google_Analytics_data/client_secrets.json ^C
```
