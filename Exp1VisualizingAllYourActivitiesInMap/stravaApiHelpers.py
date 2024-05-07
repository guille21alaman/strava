import requests
import json
import time
import datetime
import logging
logger = logging.getLogger(__name__)



#define a function for an api safe call with max retries and sleep time
def api_safe_call(url:str, max_retries=5, sleep_time=60*15+1):
    """
        Make a safe api call with max retries and sleep time
    """
    response = requests.get(url)
    retries = 0
    while response.status_code != 200:
        if retries > max_retries:
            raise Exception("Max retries reached. Response status code: %s" %response.status_code)
        else:
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            logger.info("Waiting 15 minutes for API to be available")
            time.sleep(sleep_time)
            response = requests.get(url)
            sleep_time = sleep_time+120 #add 2 minutes to the waiting time

    return json.loads(response.text)

def get_all_activities(access_token:str, after:int, max_activities=200):

    """
        Before and after should be epoch timestamps
    """
    
    url = "https://www.strava.com/api/v3/athlete/activities?access_token=%s&per_page=%s&after=%s" %(
        access_token, max_activities, after)
    
    response = api_safe_call(url)
    return response

    

def get_activity(activity_id, access_token):

    url = "https://www.strava.com/api/v3/activities/%s/?access_token=%s" %(activity_id,access_token)
    response = api_safe_call(url)
    return response

def get_url_photo_from_activity(activity):

    """
        Get the url of the primary photo of the activity
    """

    photo_url = activity["photos"]["primary"]["urls"]["600"]

    return photo_url
