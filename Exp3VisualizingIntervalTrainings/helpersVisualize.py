import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_hex


def get_color_palette_from_float_column(df, col_name, col_palette):
    cmap = plt.get_cmap(col_palette) #gets a color map
    norm = plt.Normalize(df[col_name].min()-0.0005*df[col_name].min(), df[col_name].max()+0.0005*df[col_name].max()) #normalizes the column 
    return df[col_name].apply(lambda x: to_hex(cmap(norm(x)), keep_alpha=True))  #returns the column with the colors depending on color map


def get_session_number(df, col_name):
    return df[col_name].rank(method="dense").astype(int) #Compute numerical data ranks (1 through n) along axis --> method="dense": assigns lowest rank in the group if same value, and increases 1 between groups

def generate_numbers_within_range_with_increment(minimum: int, maximum: int, increment=2):
    numbers = []

    # Adjust the minimum value to the nearest smaller number divisible by increment
    minimum = minimum - (minimum % increment) - increment #add other increment so that we have some margin down

    while minimum <= maximum+increment*2-1: #make sure we have at least one number above
        numbers.append(int(minimum))
        minimum += increment

    return numbers

def secs_distance_to_secs_1000m(secs, distance):
    #rule of three
    secs_1000m_equivalent = secs*(1000/distance)
    return secs_1000m_equivalent

def secs_1000_to_pace_min_km(secs):
    minutes = secs // 60
    remaining_seconds = secs % 60
    time_string = f"{int(minutes):02}:{int(remaining_seconds):02}"
    return time_string

def calculate_fastest_slowest_and_average_interval(df, col, distance):
    min_max_avg = [df[col].min(), df[col].max(), df[col].mean()]
    result = {}
    count = 0
    for i in min_max_avg:
        result[count] = "%s min/km" %(secs_1000_to_pace_min_km(secs_distance_to_secs_1000m(i,distance)))
        count+=1
    return result[0], result[1], result[2]

def transform_seconds_and_distance_to_pace(array_seconds, distance):
    array_seconds_equivalent_for_1000_meters = secs_distance_to_secs_1000m(array_seconds, distance)
    result = []
    for seconds in array_seconds_equivalent_for_1000_meters:
        time_string = secs_1000_to_pace_min_km(seconds)
        result.append(time_string)
    return result

def col_float_to_int(df, matching_string):
    cols = [c for c in df.columns if matching_string in c]
    for c in  cols:
        df[c] = df[c].astype(int, errors="ignore")
    return df 