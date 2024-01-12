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
    limit_activites = 10

    #length of the intervals to be visualized
    #TODO - Fix to identify 2000m series too!
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
            activity = strava.get_activity_by_id(activity_id)
            activity_class = Activity(activity)
            
            #discard if simple run without custom interval laps
            if len(activity["splits_metric"]) == len(activity["laps"]):
                continue
            else: 
                #loop over laps
                #check that we have the desired intervals (for instance 400m)
                #additional check to see that we are not mixing intervals with warm-up or cool down laps
                interval_lap_count = 0 #to count the interval laps
                next_rec = False #to store info about recovery after an interval
                row = {} #empty row to be added to df
                for lap in activity["laps"]:
                    if (lap["distance"] == interval_length_meters) and (int(lap["lap_index"]) != 1) and (int(lap["lap_index"]) != len(activity["laps"])):
                        interval_lap_count+=1
                        next_rec = True
                        #print tests
                        row["activity_name"] = activity["name"]
                        row["total_km"] = activity["distance"]/1000 #convert meters to km
                        row["date_timestamp"] = pd.to_datetime(activity["start_date_local"]).timestamp()
                        row["activity_id"] = activity["id"]
                        #NOTE: proxy to get location. Gotten via the location of one of the segments - If no segments, then null
                        location_proxy = activity_class.get_proxy_location()

                        row["location"] = "%s, %s (%s)" %(location_proxy[0],location_proxy[1],location_proxy[2])
                        row["lap"] = interval_lap_count
                        row["distance"] = lap["distance"]
                        row["seconds"] = lap["elapsed_time"] #time to complete the 400m
                        if activity["has_heartrate"] == True:
                            row["average_heartrate"], row["maximum_heartrate"] = lap["average_heartrate"], lap["max_heartrate"]
                        row["elevation_gain_interval"] = lap["total_elevation_gain"]
                        
                    elif next_rec == True:
                        row["rest_distance"] = lap["distance"]
                        if activity["has_heartrate"] == True: 
                            row["recovery_average_heartrate"], row["recovery_maximum_heartrate"] = lap["average_heartrate"], lap["max_heartrate"]
                        next_rec = False
                        #append row to df only after information about recovery has been gathered
                        df = df._append(row, ignore_index=True)
                        row = {} #reset row

df.to_csv("Exp3VisualizingIntervalTrainings/data/intervals%sm.csv" %interval_length_meters, sep=";", index=False)

