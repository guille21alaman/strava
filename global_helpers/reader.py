#imports
import json
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from global_helpers.logger import logger

def read_all_activities():
    # Read all activivities from json files in global_data/all_activities
    # Format of files is: timestamp_%s_activity_id_%s.json
    # Loop over files and return a list of all activities
    activities = []
    for file in os.listdir('global_data/all_activities'):
        with open('global_data/all_activities/' + file) as f:
            activities.append(json.load(f))
            logger.debug(f"Activity read: {file}")
    logger.info(f"Activities read. Total amount: {len(activities)}")
    return activities


def read_activity_details(activity_id):
    # Read details of a specific activity
    # Format of file is: timestamp_%s_activity_id_%s_details.json
    # Match the activity through id
    # Return the details of the activity
    for file in os.listdir('global_data/details'):
        if str(activity_id) in file:
            with open('global_data/details/' + file) as f:
                logger.debug(f"Details read: {file}")
                return json.load(f)
