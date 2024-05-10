# Append parent folder to path
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#generic imports
from client.accessToken import *
from client.getActivities import *
from global_helpers.logger import logger
from extractor.extract_all_activities import Extractor

def extract_data(global_data_folder):

    logger.info("Extracting data")

    #refress access token strava api
    refresh_access_token()

    # Configure OAuth2 access token for authorization: strava_oauth
    access_token = os.getenv('ACCESS_TOKEN')

    #start strava class
    strava = StravaApi(access_token)

    #run while loop until all activities that were not activites to extract anymore
    global_data_folder = f"{global_data_folder}"
    extractor = Extractor(strava, global_data_folder)

    #run extractor functions
    extractor.extract_all_activities()
    extractor.extract_all_activity_details()

