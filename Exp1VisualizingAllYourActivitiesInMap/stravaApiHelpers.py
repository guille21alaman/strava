import requests
import json


def get_all_activities(access_token, max_activities):
    
    url = "https://www.strava.com/api/v3/athlete/activities?access_token=%s&per_page=%s" %(access_token, max_activities)
    response = requests.get(url)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception("Reponse from API incorrect: %s" %response.status_code)


def get_url_photo_from_activity(activity_id, access_token):

    url = "https://www.strava.com/api/v3/activities/%s/?access_token=%s" %(activity_id,access_token)
    response = requests.get(url)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        photo_url = json.loads(response.text)["photos"]["primary"]["urls"]["600"]
        return photo_url
    else:
        raise Exception("Reponse from API incorrect: %s" %response.status_code)
