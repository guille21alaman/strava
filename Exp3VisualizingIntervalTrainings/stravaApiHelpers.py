import requests
import json

class Strava:
    def __init__(self, access_token, max_activities=200):
        self.access_token = access_token
        self.max_activities = max_activities


    def get_activity_by_id(self, activity_id):
        url = "https://www.strava.com/api/v3/activities/%s?access_token=%s" %(activity_id, self.access_token)
        response = requests.get(url)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception("Reponse from API incorrect: %s" %response.status_code)

    def get_all_activities(self):
        
        url = "https://www.strava.com/api/v3/athlete/activities?access_token=%s&per_page=%s" %(self.access_token, self.max_activities)
        response = requests.get(url)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception("Reponse from API incorrect: %s" %response.status_code)


    def get_url_photo_from_activity(self, activity_id):

        url = "https://www.strava.com/api/v3/activities/%s/?access_token=%s" %(activity_id,self.access_token)
        response = requests.get(url)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            photo_url = json.loads(response.text)["photos"]["primary"]["urls"]["600"]
            return photo_url
        else:
            raise Exception("Reponse from API incorrect: %s" %response.status_code)


class Activity:
    def __init__(self, activity):
        self.activity = activity

    def get_proxy_location(self):
        """
            Gets proxy location using one of the segments through which the run was made (if exists)
            The reason to do it like this is that location_country seems to be always Austria, regardless of where the run was made
            There doesn't seem to be any other location attribute coming from the API response of get_activity
        """
        segment_efforts = self.activity["segment_efforts"]

        if len(segment_efforts)<0:
            return "Unknown","Unknown","Unknown"
        else:
            return [segment_efforts[0]["segment"]["city"], segment_efforts[0]["segment"]["state"], segment_efforts[0]["segment"]["country"]]
        