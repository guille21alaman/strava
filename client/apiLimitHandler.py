import os, sys
import requests
import json
import time
from global_helpers.logger import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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