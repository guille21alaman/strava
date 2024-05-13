# Append parent folder to path
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from global_helpers.logger import logger
from client.apiLimitHandler import *

class StravaApi: 

    #create a class for the strava api with the access token
    def __init__(self, access_token:str):
        self.access_token = access_token
    
    def get_all_activities(self, after:int, max_activities=200):

        """
            Extract all activities of a user after a certain date
            Before and after should be epoch timestamps
        """
        
        url = "https://www.strava.com/api/v3/athlete/activities?access_token=%s&per_page=%s&after=%s" %(
            self.access_token, max_activities, after)
        
        response = api_safe_call(url)
        return response

    def get_activity_details(self, activity_id:str):

        """
            Get the details of an activity by its id
        """

        url = "https://www.strava.com/api/v3/activities/%s/?access_token=%s" %(
            activity_id,self.access_token)
        
        response = api_safe_call(url)
        return response
