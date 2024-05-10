# Append parent folder to path
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#generic imports
from client.accessToken import *
from client.getActivities import *
from helpers.helpers import *
from global_helpers.logger import logger
from extractor.main import *
global_data_folder = "global_data"
output_folder = "output"

# custom imports
import polyline #to decode polylines
import folium #to draw maps using folium
import branca #for colormap
import datetime


#draw generic map with the desired coordinates
city_coordinates = [48.20867108740751, 16.392405856589747] #Example: Vienna - lat,lon
all_activities_map = folium.Map(
    location = city_coordinates,
	zoom_start = 13, 
    tiles='cartodb positron') #all available tiles: https://leaflet-extras.github.io/leaflet-providers/preview/ 
                              # Docu: https://python-visualization.github.io/folium/latest/user_guide/raster_layers/tiles.html

# Marker examples
draw_marker([48.177577, 16.3691222], popup="Favoriten", icon="glyphicon glyphicon-home", map=all_activities_map, color="black")

#read all activities in data folder into a list of json objects
all_activities = []
logger.info("Reading Activity files...")
for file in os.listdir(global_data_folder):
    if file.endswith(".json") and file.endswith("details.json")==False:
        with open("%s/%s" %(global_data_folder,file), "r") as f:
            all_activities.append(json.loads(f.read()))

#generate color map based on distance that will be used to color the routes
max_distance = 0
for a in all_activities:
    if (a["distance"] > max_distance) and (a["type"] == "Run"):
        max_distance = a["distance"]
colormap = branca.colormap.linear.GnBu_07.scale(0, max_distance)
colormap.caption = 'Distance in Meters'
colormap.add_to(all_activities_map) #add legend to the map


exit(0)

#loop over all activities
#decode coordinates
#draw information in the map
#add image if the activity has an image
folder_activity_details = f"{global_data_folder}//details/"
logger.info(f"Plotting Activities. Total: {len(all_activities)}")
for a in all_activities:
    decoded_coordinates = polyline.decode(a["map"]["summary_polyline"])  #output (lat, lon)

    if (decoded_coordinates) and (a["type"] == "Run"): #make sure it is a run and we have the coordinates
        
        activity_id = a["id"]

        #extract and store activity details if not already stored
        start_date = datetime.datetime.strptime(a["start_date"], "%Y-%m-%dT%H:%M:%SZ")
        start_date = int(start_date.timestamp())
        if not os.path.exists("%s/timestamp_%s_activity_id_%s_details.json" %(folder_activity_details, start_date, activity_id)):
            activity = strava.get_activity_details(activity_id=a["id"])
            with open("%s/timestamp_%s_activity_id_%s_details.json" %(folder_activity_details, start_date, activity_id), "w") as f:
                f.write(json.dumps(activity))
        else:
            with open("%s/timestamp_%s_activity_id_%s_details.json" %(folder_activity_details,start_date, activity_id), "r") as f:
                activity = json.loads(f.read())

        if a["total_photo_count"] > 0:
            image_url = get_primary_photo_of_activity(activity)
        else:
            image_url = "https://dgtzuqphqg23d.cloudfront.net/9rYmBQpYavDjTHRjsWbijLusrEdxLbzUqclrhtY9kXQ-1536x2048.jpg"

        html = """
            <h1 style="text-align: center;">%s</h1>
            <p style="text-align: center;"><strong>Total distance:</strong> %skm</p>
            <p style="text-align: center;"><strong>Average Speed:</strong> %skm/h</p>
            <p style="text-align: center;"><strong>Total Elevation gain:</strong> %sm</p>
            <p style="text-align: center;"><strong>Total Date:</strong> %s</p>
            <img style="text-align: center; width: 400px; height: auto;" src="%s" alt="No image available for this activity">

        """ % (
            a["name"],
            round(a["distance"]/1000, 2),
            round(3.6*a["average_speed"],2),
            round(a["total_elevation_gain"],2),
            start_date,
            image_url)

        #add image to the popup if it exists (if not simple pop up with other infp)
        iframe = branca.element.IFrame(html, width=450, height=550)
        popup = folium.Popup(iframe, max_width=500)
        
        #add routes to the map with color depending on distance
        folium.PolyLine(locations = decoded_coordinates, 
                    line_opacity = 0.1, popup=popup, color=colormap(a["distance"])).add_to(all_activities_map) 

logger.info("Saving Map...")   

#save map in html file
all_activities_map.save(f"{output_folder}/all_activities_map.html")
