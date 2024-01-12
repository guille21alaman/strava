import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_hex


def get_color_palette_from_float_column(df, col_name, col_palette):
    cmap = plt.get_cmap(col_palette) #gets a color map
    norm = plt.Normalize(df[col_name].min()-0.0005*df[col_name].min(), df[col_name].max()+0.0005*df[col_name].max()) #normalizes the column #TODO Smooth cleaner
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

def transform_seconds_and_distance_to_pace(array_seconds, distance):
    array_seconds_equivalent_for_1000_meters = array_seconds*(1000/distance) #rule of three
    result = []
    for seconds in array_seconds_equivalent_for_1000_meters:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        time_string = f"{int(minutes):02}:{int(remaining_seconds):02}"
        result.append(time_string)
    return result

