import folium

def draw_marker(coordinates, popup, map, color="black", icon="glyphicon glyphicon-record"):
    folium.Marker(
    coordinates, 
	popup = popup, 
    icon=folium.Icon(color=color, icon=icon) #all icons: https://www.w3schools.com/bootstrap/bootstrap_ref_comp_glyphs.asp
    ).add_to(map)