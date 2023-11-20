import datetime

def to_min_per_km(speed_in_ms: float, distance_in_meters: float):
    #transform speed and distance into duration in seconds
    duration_in_s = distance_in_meters/speed_in_ms
    #convert to timedelta
    return datetime.timedelta(seconds=duration_in_s)

def format_timedelta(td: datetime.timedelta):
    minutes, seconds = divmod(td.total_seconds(), 60)
    return f"{int(minutes):02d}:{int(seconds):02d}"

def extract_pace_zone(speed_in_min_per_km: datetime.timedelta):
    #approximate references
    zone_1 = datetime.timedelta(seconds=5*60+20) #5:20
    zone_2 = datetime.timedelta(seconds=4*60+44) #4:44
    zone_3 = datetime.timedelta(seconds=4*60+29) #4:29
    zone_4 = datetime.timedelta(seconds=4*60+16) #4:16
    zone_5 = datetime.timedelta(seconds=3*60+42) #3:42 - #not needed
    zones = [zone_1, zone_2, zone_3, zone_4, zone_5]

    #append to list
    zones.append(speed_in_min_per_km)
    #sort descending 
    zones = sorted(zones, reverse=True)
    #extract index in list +1 = zone (up to 6 zones if faster than 5)
    return "Zone" + str(zones.index(speed_in_min_per_km)+1)
    



