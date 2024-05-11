# Append parent folder to path
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#generic imports
from helpers.helpers import *
from global_helpers.logger import logger
from global_helpers.reader import read_all_activities, read_activity_details
from extractor.main import *
global_data_folder = "global_data"
output_folder = "output"

# custom imports
import polyline #to decode polylines
import folium #to draw maps using folium
import datetime

#update extracted data
extract_data(global_data_folder=global_data_folder)

#read data
all_activities = read_all_activities()

#draw generic map with the desired coordinates
city_coordinates = [48.20867108740751, 16.392405856589747] #Example: Vienna - lat,lon
all_activities_map = folium.Map(
    location = city_coordinates,
	zoom_start = 13, 
    tiles='cartodb positron') #all available tiles: https://leaflet-extras.github.io/leaflet-providers/preview/ 
                              # Docu: https://python-visualization.github.io/folium/latest/user_guide/raster_layers/tiles.html

# Home Marker
draw_marker(
    coordinates=[48.177577, 16.3691222], 
    popup="Favoriten", 
    icon="glyphicon glyphicon-home", 
    map=all_activities_map, 
    color="black")


#extract max distance of activities and set color map
max_distance = extract_max_distance(all_activities)
colormap, all_activities_map = generate_colormap(max_distance, all_activities_map)

#loop over all activities
#decode coordinates
#draw information in the map
#add image if the activity has an image
logger.info(f"Plotting Activities. Total: {len(all_activities)}")

#max_start_date_timpestamp flag
#start max_start_date with year 0
# initialize max_start_date with year 0
max_start_date = datetime.datetime(1, 1, 1)
for a in all_activities:
    decoded_coordinates = polyline.decode(a["map"]["summary_polyline"])  #output (lat, lon)
    if (decoded_coordinates) and (a["type"] == "Run"): #make sure it is a run and we have the coordinates
        activity_id = a["id"]

        #read activiy details
        activity_details = read_activity_details(activity_id)

        #extract and store activity details if not already stored
        start_date = datetime.datetime.strptime(a["start_date"], "%Y-%m-%dT%H:%M:%SZ")

        #keep track of latest timestamp
        if max_start_date > start_date:
            max_start_date = start_date

        #get primary photo of activity (if available)
        if a["total_photo_count"] > 0:
            image_url = get_primary_photo_of_activity(activity_details)
        else:
            image_url = "https://dgtzuqphqg23d.cloudfront.net/9rYmBQpYavDjTHRjsWbijLusrEdxLbzUqclrhtY9kXQ-1536x2048.jpg"

        #create popup with activity information
        html = """
            <h1 style="text-align: center;">%s</h1>
            <p style="text-align: center;"><strong>Total distance:</strong> %skm</p>
            <p style="text-align: center;"><strong>Average Speed:</strong> %skm/h</p>
            <p style="text-align: center;"><strong>Total Elevation gain:</strong> %sm</p>
            <p style="text-align: center;"><strong>Date:</strong> %s</p>
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
directory =__file__.split("\\")[-2]
all_activities_map.save(f"{directory}/{output_folder}/all_activities_map_%s.html" %(start_date.strftime("%d_%m_%Y")))

