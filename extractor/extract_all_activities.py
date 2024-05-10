import os, sys
import datetime
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from global_helpers.logger import logger
from client.getActivities import StravaApi


class Extractor:

    #intialize class
    def __init__(self, strava_api_class, global_data_folder):
        self.strava = strava_api_class
        self.global_data_folder = global_data_folder
        pass

    def extract_all_activities(self):
        stored = True
        self.all_activities_folder = self.global_data_folder + "/all_activities/"
        #Also if nothing to update, nothing should be call to API
        while (stored==True):
            #in a folder, there are existing activities stored with format timestamp_%s_activity_id_%s.json
            #find the latest timestamp
            #if there is no file then set timestamp to 0
            #store also a list of all activity ids that are already stored
            activity_ids = []
            latest_timestamp = 0
            for file in os.listdir(self.all_activities_folder):
                activity_ids.append(file.split("_")[4].split(".")[0])
                if file.endswith(".json"):
                    timestamp = int(file.split("_")[1])
                    if timestamp > latest_timestamp:
                        latest_timestamp = timestamp
            #get all activities from strava api
            logger.info(f"Extracting activities from Strava API... Latest Timestamp: {latest_timestamp}")
            extracted_activities = self.strava.get_all_activities(after=latest_timestamp, max_activities=200)

            #store each of the activities in a json file under data folder
            #file format should include the activity id and the epoch timestamp of the start_dates
            #add additional check to make sure that the activity id is not already stored
            for a in extracted_activities:
                start_date = datetime.datetime.strptime(a["start_date"], "%Y-%m-%dT%H:%M:%SZ")
                start_date = int(start_date.timestamp())
                activity_id = a["id"]
                if str(activity_id) in activity_ids:
                    stored = False #no activity stored (if all like this, the iteration will stop)
                else:
                    logger.debug(f"Storing activity with id {activity_id} and name {a['name']}")
                    with open("%s/timestamp_%s_activity_id_%s.json" %(self.all_activities_folder,start_date, activity_id), "w") as f:
                        f.write(json.dumps(a))
                    #activity was stored
                    stored = True

    def extract_all_activity_details(self):
        details_folder = self.global_data_folder + "/details/"
        #read all activities in data folder into a list of json objects
        all_activities = []
        logger.info("Reading Activity files...")
        for file in os.listdir(self.all_activities_folder):
            if file.endswith(".json") and file.endswith("details.json")==False:
                with open("%s/%s" %(self.all_activities_folder,file), "r") as f:
                    all_activities.append(json.loads(f.read()))
        
        logger.info("Extracting Activity Details...")
        for a in all_activities:        
            activity_id = a["id"]
            #extract and store activity details if not already stored
            start_date = datetime.datetime.strptime(a["start_date"], "%Y-%m-%dT%H:%M:%SZ")
            start_date = int(start_date.timestamp())
            if not os.path.exists("%s/timestamp_%s_activity_id_%s_details.json" %(details_folder, start_date, activity_id)):
                activity = self.strava.get_activity_details(activity_id=a["id"])
                with open("%s/timestamp_%s_activity_id_%s_details.json" %(details_folder, start_date, activity_id), "w") as f:
                    f.write(json.dumps(activity))
            else:
                with open("%s/timestamp_%s_activity_id_%s_details.json" %(details_folder,start_date, activity_id), "r") as f:
                    activity = json.loads(f.read())