import os 
from stravaApiHelpers import *
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
import pandas as pd 
import numpy as np
from bokeh.palettes import Reds256
from bokeh.models import LinearColorMapper
from bokeh.transform import transform
from bokeh.colors import Color
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex



if __name__ == "__main__":
    
    #limit activities to get from API - could be also filtered by date
    limit_activites = 50

    #length of the intervals to be visualized
    interval_length_meters = 400

    # Configure OAuth2 access token for authorization: strava_oauth
    access_token = os.getenv('ACCESS_TOKEN')

    #initialize Strava Class
    strava = Strava(access_token, max_activities=limit_activites)

    #get all activities
    activities = strava.get_all_activities()

    #dataframe
    df = pd.DataFrame(columns=[
        "date_timestamp","activity_id","location","activity_name",
        "lap","distance","seconds","rest_distance","total_km","elevation_gain_interval",
        "average_heartrate", "max_heartrate"])

    for a in activities:
        #check that it is a run
        if a["type"] == "Run":
            activity_id = a["id"]
            activity_json = strava.get_activity_by_id(activity_id)
            activity = Activity(activity_json, interval_length_meters)
            print(activity.activity["name"])
    
            #discard if simple run without custom interval laps
            if activity.check_split_len_equals_lap_length():
                continue
            #here we have only runs that are already a interval workout
            #we need to filter only those we are aiming for
            else:
                df = activity.check_matching_interval_and_return_laps(df)

df.to_csv("Exp3VisualizingIntervalTrainings/data/intervals%sm.csv" %interval_length_meters, sep=";", index=False)

