import folium
import branca #for colormap

def draw_marker(coordinates, popup, map, color="black", icon="glyphicon glyphicon-record"):
    folium.Marker(
    coordinates, 
	popup = popup, 
    icon=folium.Icon(color=color, icon=icon) #all icons: https://www.w3schools.com/bootstrap/bootstrap_ref_comp_glyphs.asp
    ).add_to(map)

def get_primary_photo_of_activity(activity:dict):

    """
        Get the url of the primary photo of the activity
    """

    photo_url = activity["photos"]["primary"]["urls"]["600"]

    return photo_url

def extract_max_distance(all_activities):
    max_distance = 0
    for a in all_activities:
        if (a["distance"] > max_distance) and (a["type"] == "Run"):
            max_distance = a["distance"]
    return max_distance

def generate_colormap(max_distance,map):
    colormap = branca.colormap.linear.GnBu_07.scale(0, max_distance)
    colormap.caption = 'Distance in Meters'
    colormap.add_to(map) #add legend to the map
    return colormap, map