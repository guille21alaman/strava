import os #for env variable
from stravaApiHelpers import *
from helpers import *
import pandas as pd

norway = True
if norway == True:
    #norweigan zones
    zone_1 = datetime.timedelta(seconds=4*60+55) #4:45 or above (Easy)
    zone_2 = datetime.timedelta(seconds=4*60+44) #4:05-4:44 (Threshold)
    # more than 4:05 anaerobic 
    zones = [zone_1, zone_2]
    zones_names = ["Easy", "Threshold", "Anaerobic"]

else:
    #approximate references for zones
    zone_1 = datetime.timedelta(seconds=5*60+20) #5:20 (Recovery-Easy)
    zone_2 = datetime.timedelta(seconds=4*60+44) #4:44 4:44-5:20 (Aerobic-Base)
    zone_3 = datetime.timedelta(seconds=4*60+29) #4:29-4:44 (Tempo)
    zone_4 = datetime.timedelta(seconds=4*60+16) #4:16-4:29 (Lactate Threshold)
    zone_5 = datetime.timedelta(seconds=3*60+42) #4:16-3:42 (Anaerobic)
    #zone_6 = There is always an automatic zone created (i.e. >zone 5) - (Anaerobic Plus)
    zones = [zone_1, zone_2, zone_3, zone_4, zone_5]
    zones_names = ["Recovery-Easy","Aerobic-Base","Tempo","Lactate Threshold","Anaerobic", "Anaerobic Plus"]

if len(zones_names) != 0:
    assert len(zones)+1 == len(zones_names)
    

if __name__ == "__main__":
    
    # Configure OAuth2 access token for authorization: strava_oauth
    access_token = os.getenv('ACCESS_TOKEN')

    #limit activities to get from API - could be also filtered by date
    limit_activites = 50

    #get all activities
    activities = get_all_activities(access_token, limit_activites)

    #df
    df = pd.DataFrame(columns=[
        "activity_id", "date","distance_in_m", "split_no", 
        "average_speed_formatted", "adjusted_grade_speed_formatted", "average_speed", "adjusted_grade_speed",
        "elevation_difference_in_m","location","activity_type"])

    for a in activities:
        activity_type = a["type"]
        if activity_type == "Run":
            print("Activity: ", a["name"])
            activity = get_activity_by_id(access_token, int(a["id"]))
            date = pd.to_datetime(activity["start_date"])
            location = activity["location_country"]
            id = activity["id"]
            for split in activity["splits_metric"]:
                #if split is approx 1000m (give some room for error)
                if (990 < split["distance"] < 1010):
                    new_row = {}
                    new_row["activity_id"], new_row["date"], new_row["distance_in_m"], new_row["location"], new_row["activity_type"] = id, date, split["distance"], location, activity_type
                    new_row["split_no"] = split["split"]
                    #introducing paces and cleaning them
                    new_row["average_speed"] = to_min_per_km(split["average_speed"], split["distance"])
                    new_row["average_speed_formatted"] = format_timedelta(new_row["average_speed"])
                    #Grade Adjusted Pace takes into account the steepness of terrain during your runs and estimates an equivalent pace on flat land: https://support.strava.com/hc/en-us/articles/216917067-Grade-Adjusted-Pace-GAP-
                    new_row["adjusted_grade_speed"] = to_min_per_km(split["average_grade_adjusted_speed"], split["distance"])
                    new_row["adjusted_grade_speed_formatted"] = format_timedelta(new_row["adjusted_grade_speed"])
                    new_row["elevation_difference_in_m"] = split["elevation_difference"]
                    #add trianing zones if heart rate not available
                    if split["pace_zone"] == 0:
                        new_row["pace_zone"], zones = extract_pace_zone(new_row["average_speed"], zones)
                    else:
                        new_row["pace_zone"] = split["pace_zone"]
                            
                    df = df._append(new_row, ignore_index=True)
        else:
            print("Not a run: ", activity_type)

    df = df.sort_values(by=["average_speed"], ascending=True)
    df.to_csv("Exp2VisualizingPacePerKm/data/AllTime1kmSplits.csv", index=False, header=True, sep=";", decimal=",")
