#internal modules
from stravaApiHelpers import *
from helpersVisualize import *

#external libs
# import streamlit as st
import pandas as pd 
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.models import LinearAxis, FixedTicker, Range1d, HoverTool


###################
# TRANSFORMATIONS #
###################

#read file
interval_length_meters = 400
df = pd.read_csv("Exp3VisualizingIntervalTrainings/data/intervals%sm.csv" %interval_length_meters, sep=";")

#column pace as string (needed later on)
df["pace"] = transform_seconds_and_distance_to_pace(array_seconds=df["seconds"].values, distance=interval_length_meters)

#assign colors depending on date timestamps
df["date_color"] = get_color_palette_from_float_column(df, "date_timestamp", "Reds") #matplotlib colormaps: https://matplotlib.org/stable/users/explain/colors/colormaps.html

#create a column with date in readable format
df["date"] = pd.to_datetime(df["date_timestamp"], unit="s").dt.date

#specify the order of the intervals based on date (i.e., first time this session was done is 1, second time is 2, etc.)
df["session_no"] = get_session_number(df, "date")

#sort by session number and lap
df = df.sort_values(by=["session_no","lap"])

#convert session_no to str to avoid problems when joining cols later
df["session_no"] = "session_" + df["session_no"].astype(str)


#column selection
df = df[[
    "lap", 
    "session_no", 
    "seconds","distance","pace",
    "date_color","date","location", "activity_id","activity_name","total_km","elevation_gain_interval",
    "average_heartrate","maximum_heartrate","recovery_average_heartrate","recovery_maximum_heartrate"]]

#extract fastest and slowest lap for later usage in extra y axis
fastest_lap, slowest_lap = df["seconds"].max(), df["seconds"].min()
if df["distance"].nunique() == 1:
    distance = df["distance"].unique()[0]
else:
    raise ValueError("Several distances in the intervals!")
array_y_ticks = np.array(generate_numbers_within_range_with_increment(slowest_lap, fastest_lap))
array_y_ticks_pace = transform_seconds_and_distance_to_pace(array_y_ticks,distance)


#pivoting the table to visualize (each row represents one of the 10 laps, each column contains the data of each run)
df = df.pivot(index='lap',
               columns=['session_no'],
               values=['seconds','date','date_color','location', "pace",
                       'distance',"activity_id","activity_name","total_km", "elevation_gain_interval",
                       "average_heartrate","maximum_heartrate","recovery_average_heartrate","recovery_maximum_heartrate"])
df = df.reset_index()
df.columns = ['_'.join(reversed(col)).strip() if "" not in col else "".join(col).strip() for col in df.columns.values] #if else to avoid lap to be stored like "lap_" #also reversed to have session_x_seconds instead of seconds_session_x


#transform heartrate columns to int
df = col_float_to_int(df=df, matching_string="heartrate")

#################
# VISUALIZATION #
#################

#set x and y columns for visualization
x="lap"
y="seconds"


# create a new plot with a title and axis labels
p = figure(
    title="Visualization %s Intervals" %interval_length_meters, 
    x_axis_label=x.capitalize(), 
    y_axis_label=y.capitalize(), 
    width=1500,
    height=650) 

#params figure
p.xaxis.ticker = df["lap"].unique() #set xaxis ticks custom
#y ticks with seconds and pace
p.yaxis.ticker = array_y_ticks
override = {}
for i in range(0,len(array_y_ticks)):
    override[array_y_ticks[i]] = "%ss - %smin/km" %(array_y_ticks[i],array_y_ticks_pace[i])
p.yaxis.major_label_overrides = override
p.y_range.flipped = True #flip range (faster looks higher - i.e. less seconds)

#y variable names list
y_variable_names =  [col for col in df.columns if y in col]

#loop over columns to plot circles and lines
for col in y_variable_names:
    str_to_remove = "_"+y # _seconds str from y column
    session_no = col.replace(str_to_remove, "")
    color = df['%s_date_color' %session_no].unique()[0] #remove seconds_ from y column (i.e., keep only the session_x str) - add it to date_color to set the right color
    #legend config
    legend_session = session_no.replace("_"," ").capitalize()
    legend_date = df[session_no+"_date"].unique()[0].strftime("%d-%m-%Y")
    legend_location = df[session_no+"_location"].unique()[0]
    legend_activity_id = df[session_no+"_activity_id"].unique()[0]
    legend_ref_name = legend_session+": "+legend_date+" - %s" %legend_location + " - ID: %s" %legend_activity_id
    #hover stats
    fastest_interval, slowest_interval, average_interval = calculate_fastest_slowest_and_average_interval(df, "%s_seconds" %session_no, distance=interval_length_meters)
    total_km_round = round(df["%s_total_km" %session_no].unique()[0],2)
    average_elevation_gain_session = round(df["%s_elevation_gain_interval"%session_no].mean(),2)
    circle= p.circle(
        x=x, 
        y=col, 
        source=df,
        fill_color=color,
        color=color,
        size=20,
        legend_label="%s" %legend_ref_name
        )
    circle_hover = HoverTool(renderers=[circle], tooltips=[
        ("Lap: ","@lap"),
        ("Pace: ", "@%s_pace min/km" %session_no),
        ("Elevation Gain in Lap: ", "@%s_elevation_gain_interval m" %session_no),
        ("Average Heart Rate Within Interval: ", "@%s_average_heartrate bpm" %session_no),
        ("Average Heart Rate Within Rest: ", "@%s_recovery_average_heartrate bpm" %session_no),
        ("Maximum Heart Rate Within Interval: ", "@%s_maximum_heartrate bpm" %session_no),
        ("Maximum Heart Rate Within Rest: ", "@%s_recovery_maximum_heartrate bpm" %session_no),

        ])
    p.add_tools(circle_hover)
    line = p.line(
        x=x, 
        y=col, 
        source=df, 
        color=color, 
        line_width=5,
        legend_label="%s" %legend_ref_name
        )
    line_hover = HoverTool(renderers=[line], tooltips=[
        ("Activity Name: ", "@%s_activity_name" %session_no),
        ("Date: ", "%s" %legend_date),
        ("Total km in the activity: ", "%s km" %total_km_round),
        ("Seconds: ","@%s_seconds seconds" %session_no),
        ("Slowest Interval: ", "%s" %slowest_interval),
        ("Fastest Interval: ", "%s" %fastest_interval),
        ("Average Pace: ", "%s" %average_interval),
        ("Average Elevation Gain in Intervals", "%s" %average_elevation_gain_session),
        ])
    p.add_tools(line_hover)

#other params figure
p.legend.location = "top_left" #more legend configs; https://docs.bokeh.org/en/latest/docs/first_steps/first_steps_3.html 
output_file("Exp3VisualizingIntervalTrainings/output/%sm.html" %interval_length_meters) #output location

# Show rendering
show(p)
# st.bokeh_chart(p, use_container_width=True) #https://github.com/streamlit/streamlit/issues/5858