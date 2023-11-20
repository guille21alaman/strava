import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from helpers import format_timedelta

df = pd.read_csv("Exp2VisualizingPathPerKm/data/AllTime1kmSplits.csv",
                sep=";", decimal=",", parse_dates=["date"])
#correct dtypes
df['average_speed'] = pd.to_timedelta(df['average_speed'])
df['adjusted_grade_speed'] = pd.to_timedelta(df['adjusted_grade_speed'])
df['pace_zone'] = df['pace_zone'].astype(str)
df["pace_zone"] = df["pace_zone"].replace({
    "Zone1":'Zone1 (Recovery-Easy)',
    "Zone2":'Zone2 (Aerobic-Base)',
    "Zone3":'Zone3 (Tempo)',
    "Zone4":'Zone4 (Lactate Threshold)',
    "Zone5":'Zone5 (Anaerobic)',
    "Zone6":"Zone6 (Anaerobic +)"
})

def plot_pace_zones(df):
    # Define the order of pace zones
    pace_zone_order = ['Zone1 (Recovery-Easy)', 'Zone2 (Aerobic-Base)', 'Zone3 (Tempo)', 'Zone4 (Lactate Threshols)', 'Zone5 (Anaerobic)', "Zone6 (Anaerobic +)"]

    # Find the pace zone with the highest count
    max_count_pace_zone = df['pace_zone'].value_counts().idxmax()

    # Create a color palette
    colors = ['skyblue' if pace_zone != max_count_pace_zone else 'orange' for pace_zone in pace_zone_order]

    # Create a figure and axis
    plt.figure(figsize=(15, 8))
    ax = sns.countplot(data=df, x='pace_zone', order=pace_zone_order, palette=colors)
    plt.title('Absolute Frequency of Pace Zones\n From: %s to %s' %(df["date"].min().strftime('%d-%m-%Y'), df["date"].max().strftime('%d-%m-%Y')),
            fontsize=16, fontweight='bold')
    plt.xlabel('Pace Zone', fontsize=14)
    plt.ylabel('Count of 1Km Splits at this pace', fontsize=14)

    # Annotate with average speed
    total_count = df['pace_zone'].count()
    for i, pace_zone in enumerate(pace_zone_order):
        count = df['pace_zone'].value_counts()[pace_zone]
        percentage = count/total_count
        avg_speed = df[df['pace_zone'] == pace_zone]['average_speed'].mean()
        avg_speed = format_timedelta(avg_speed)
        ax.text(i, count + 5, f'Count: {count} ({round(percentage*100,2)}%)\nAvg Speed: {avg_speed}', ha='center', fontsize=12)

    plt.ylim(0, df['pace_zone'].value_counts().max() + 30)  # You can adjust the +2 for more space at the top

    # Show the plot
    plt.savefig('Exp2VisualizingPathPerKm/vis/pace_zones_plot.png', bbox_inches='tight')


#plot pace zones
plot_pace_zones(df)