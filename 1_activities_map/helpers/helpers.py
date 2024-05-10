import folium

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