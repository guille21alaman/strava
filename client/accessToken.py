import os
import json
import requests
from dotenv import load_dotenv

def refresh_access_token():

    #read env variables from .env file
    load_dotenv()
    
    # Get the env variables
    clientId = os.getenv('CLIENT_ID')
    clientSecret = os.getenv('CLIENT_SECRET')
    authorizationCode = os.getenv('AUTHORIZATION_CODE')
    refreshToken = os.getenv('REFRESH_TOKEN')

    # Make a post request to the api
    url = f"https://www.strava.com/oauth/token?client_id={clientId}&client_secret={clientSecret}&code={authorizationCode}&grant_type=refresh_token&refresh_token={refreshToken}"
    response = requests.post(url)

    #extract access_token from response
    response = response.json()
    access_token = response['access_token']

    # Store the response text as an environmental variable
    os.environ['ACCESS_TOKEN'] = access_token
