import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from helpers import format_timedelta
import datetime
from main import zones, zones_names

#zones naming
zones_naming = {}

for i in range(len(zones)+1):
    if i==0:
        lower =  str(zones[i])[-5:]
        zones_naming["Zone%s" %(i+1)] = "Zone%s:\n > %s" %(i+1, lower)
    elif i>0 and i<len(zones):
        upper =  str(zones[i-1])[-5:]
        lower = str(zones[i])[-5:]
        zones_naming["Zone%s" %(i+1)] = "Zone%s:\n %s-%s" %(i+1, lower, upper)
    else: 
        upper = str(zones[i-1])[-5:]
        zones_naming["Zone%s" %(i+1)] = "Zone%s:\n < %s" %(i+1, upper)

if len(zones_names) != 0:
    c=0
    for z in zones_naming:
        zones_naming[z] = zones_naming[z] + "\n(%s)" %zones_names[c]
        c+=1
    
df = pd.read_csv("Exp2VisualizingPacePerKm/data/AllTime1kmSplits.csv",
                sep=";", decimal=",", parse_dates=["date"])
#correct dtypes
df['average_speed'] = pd.to_timedelta(df['average_speed'])
df['adjusted_grade_speed'] = pd.to_timedelta(df['adjusted_grade_speed'])
df['pace_zone'] = df['pace_zone'].astype(str)
df["pace_zone"] = df["pace_zone"].replace(zones_naming)

def plot_pace_zones(df, zones_naming):
    # Define the order of pace zones
    pace_zone_order=[]
    for z in zones_naming:
        pace_zone_order.append(zones_naming[z])

    # Find the pace zone with the highest count
    max_count_pace_zone = df['pace_zone'].value_counts().idxmax()

    # Create a color palette
    colors = ['skyblue' if pace_zone != max_count_pace_zone else 'orange' for pace_zone in pace_zone_order]
    
    # Create a figure and axis
    plt.figure(figsize=(15, 8))
    ax = sns.countplot(data=df, x='pace_zone', order=pace_zone_order, palette=colors)
    plt.title('Absolute Frequency of Pace Zones\n From: %s to %s\nTotal Km: %s' %(
        df["date"].min().strftime('%d-%m-%Y'),
        df["date"].max().strftime('%d-%m-%Y'),
        df.shape[0]),
            fontsize=16, fontweight='bold')
    plt.xlabel('Pace Zone', fontsize=14)
    plt.ylabel('Count of 1Km Splits at this pace', fontsize=14)

    # Annotate with average speed
    total_count = df['pace_zone'].count()
    for i, pace_zone in enumerate(pace_zone_order):
        if pace_zone in df["pace_zone"].unique():
            count = df['pace_zone'].value_counts()[pace_zone]
            percentage = count/total_count
            avg_speed = df[df['pace_zone'] == pace_zone]['average_speed'].mean()
            avg_speed = format_timedelta(avg_speed)
        else:
            count=0
            percentage=0
            avg_speed=None
        ax.text(i, count + 5, f'Count: {count} ({round(percentage*100,2)}%)\nAvg Speed: {avg_speed}', ha='center', fontsize=12)

    plt.ylim(0, df['pace_zone'].value_counts().max() + 30)  # You can adjust the +2 for more space at the top

    # Show the plot
    plt.savefig('Exp2VisualizingPacePerKm/vis/pace_zones_plot.png', bbox_inches='tight')


#plot pace zones
plot_pace_zones(df, zones_naming)