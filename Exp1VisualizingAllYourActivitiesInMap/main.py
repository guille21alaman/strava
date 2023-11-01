import polyline #to decode polylines
import folium #to draw maps using folium
import branca #for colormap
import os #for env variable
import datetime
from stravaApiHelpers import *
from mapHelpers import *


# Configure OAuth2 access token for authorization: strava_oauth
access_token = os.getenv('ACCESS_TOKEN')

#get all activities from strava api
all_activities = get_all_activities(access_token, max_activities=200)

#draw generic map with the desired coordinates
city_coordinates = [48.20867108740751, 16.392405856589747] #Example: Vienna - lat,lon
all_activities_map = folium.Map(
    location = city_coordinates,
	zoom_start = 13, 
    tiles='cartodb positron') #all available tiles: https://leaflet-extras.github.io/leaflet-providers/preview/ 
                              # Docu: https://python-visualization.github.io/folium/latest/user_guide/raster_layers/tiles.html

# Marker examples
draw_marker([48.177577, 16.3691222], popup="Favoriten", icon="glyphicon glyphicon-home", map=all_activities_map, color="black")
draw_marker([48.217337792847566, 16.3958823655762], popup="Prater", map=all_activities_map)

#generate color map based on distance that will be used to color the routes
max_distance = 0
for a in all_activities:
    if (a["distance"] > max_distance) and (a["type"] == "Run"):
        max_distance = a["distance"]
colormap = branca.colormap.linear.GnBu_07.scale(0, max_distance)
colormap.caption = 'Distance in Meters'
colormap.add_to(all_activities_map) #add legend to the map


#loop over all activities
#decode coordinates
#draw information in the map
#add image if the activity has an image
for a in all_activities:
    decoded_coordinates = polyline.decode(a["map"]["summary_polyline"])  #output (lat, lon)

    if (decoded_coordinates) and (a["type"] == "Run"): #make sure it is a run and we have the coordinates
    
        if a["total_photo_count"] > 0:
            image_url = get_url_photo_from_activity(a["id"], access_token=access_token)
        else:
            image_url = False

        html = """
            <h1 style="text-align: center;">%s</h1>
            <p style="text-align: center;"><strong>Total distance:</strong> %skm</p>
            <p style="text-align: center;"><strong>Average Speed:</strong> %skm/h</p>
            <p style="text-align: center;"><strong>Total Elevation gain:</strong> %sm</p>
            <img style="text-align: center; width: 400px; height: auto;" src="%s" alt="No image available for this activity">

        """ % (a["name"], round(a["distance"]/1000, 2), round(3.6*a["average_speed"],2), round(a["total_elevation_gain"],2), image_url)

        #add image to the popup if it exists (if not simple pop up with other infp)
        iframe = branca.element.IFrame(html, width=450, height=550)
        popup = folium.Popup(iframe, max_width=500)
        
        #add routes to the map with color depending on distance
        folium.PolyLine(locations = decoded_coordinates, 
                    line_opacity = 0.1, popup=popup, color=colormap(a["distance"])).add_to(all_activities_map) 
        
#save map in html file
all_activities_map.save("Exp1VisualizingAllYourActivitiesInMap/all_activities_map.html")
 

 
