import requests
import json
import pandas as pd

class Strava:
    def __init__(self, access_token, max_activities=200):
        self.access_token = access_token
        self.max_activities = max_activities


    def get_activity_by_id(self, activity_id):
        url = "https://www.strava.com/api/v3/activities/%s?access_token=%s" %(activity_id, self.access_token)
        response = requests.get(url)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception("Reponse from API incorrect: %s" %response.status_code)

    def get_all_activities(self):
        
        url = "https://www.strava.com/api/v3/athlete/activities?access_token=%s&per_page=%s" %(self.access_token, self.max_activities)
        response = requests.get(url)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception("Reponse from API incorrect: %s" %response.status_code)


    def get_url_photo_from_activity(self, activity_id):

        url = "https://www.strava.com/api/v3/activities/%s/?access_token=%s" %(activity_id,self.access_token)
        response = requests.get(url)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            photo_url = json.loads(response.text)["photos"]["primary"]["urls"]["600"]
            return photo_url
        else:
            raise Exception("Reponse from API incorrect: %s" %response.status_code)


class Activity:
    def __init__(self, activity, interval_length_meters):
        self.activity = activity
        self.interval_length_meters = interval_length_meters

    def check_split_len_equals_lap_length(self):
        """
            Checks if the legnth of split metrics (1000m splits) is equal to the length of laps
            This is important, because if they differ, then there must be some kind of interval training ongoing
        """
        return len(self.activity["splits_metric"]) == len(self.activity["laps"])

    def get_proxy_location(self):
        """
            Gets proxy location using one of the segments through which the run was made (if exists)
            The reason to do it like this is that location_country seems to be always Austria, regardless of where the run was made
            There doesn't seem to be any other location attribute coming from the API response of get_activity
        """
        segment_efforts = self.activity["segment_efforts"]

        if len(segment_efforts)==0:
            return "Unknown","Unknown","Unknown"
        else:
            return [segment_efforts[0]["segment"]["city"], segment_efforts[0]["segment"]["state"], segment_efforts[0]["segment"]["country"]]

    def check_matching_interval_and_return_laps(self, df):

        """
            Calls a function that 
            1) Checks if the current activity matches the target interval type (i.e., less than 100m)
                3 types:
                    - Intervals of less than 1000m (Custom lower than 1000m)
                    - Intervals of 1000m or more with exact multiples of 1000m: 1000m,2000m,3000m, etc. (1000m or multiple intervals)
                    - Intervals of more than 1000m, but not exact multiple of 1000m: 1500m, 2200m, 3900m, etc. (Custom higher than 1000m)
            2) Depending on the type, runs a function that stores in a global df, the rows representing each interval lap (i.e., one row for each 100m interval)
        """
        
        #define df
        self.df = df
        #define some common properties (like counters)
        self.interval_lap_count = 0 #to count the interval laps
        self.next_rec = False #to store info about recovery after an interval
        self.row = {} #empty row to be added to df

        #if lenght is lower than 1000m, intervals can be identified directly
        if (0<self.interval_length_meters<1000):
            return self.get_interval_instance_of_type_custom_lower_than_1000()

        #if intervals are of 1000m or more (but always exact multiples of 1000m - i.e. 2000,3000...),
        # then identify the interval as described in the function description
        elif (self.interval_length_meters>=1000) and (self.interval_length_meters % 1000 == 0):
            return self.get_interval_instance_of_type_multiple_1000()

            #if intervals more than 1000 meters and not exact multiples of 1000m
            # then identify all multiples of 1000m first, then the exact remaining interval from interval_length_meters % 1000 != 0 + recoveries and warmups
        elif (self.interval_length_meters>1000) and (self.interval_length_meters % 1000 != 0):
            return "Custom higher than 1000m"
        
        else: 
            raise ValueError("Wrong interval entered %s" %self.interval_length_meters)
    

    def extract_generic_activity_properties(self):
        #extract generic activity properties
        self.row["activity_name"] = self.activity["name"]
        self.row["total_km"] = self.activity["distance"]/1000 #convert meters to km
        self.row["date_timestamp"] = pd.to_datetime(self.activity["start_date_local"]).timestamp()
        self.row["activity_id"] = self.activity["id"]
        return self.row
    
    def extract_recovery_properties(self,lap):
        self.row["rest_distance"] = lap["distance"]
        if self.activity["has_heartrate"] == True: 
            self.row["recovery_average_heartrate"], self.row["recovery_maximum_heartrate"] = lap["average_heartrate"], lap["max_heartrate"]
        return self.row

    def get_interval_instance_of_type_custom_lower_than_1000(self):
        #loop over laps
        #check that we have the desired intervals depending on the type (for instance 400m)
        #additional check to see that we are not mixing intervals with warm-up or cool down laps
        for lap in self.activity["laps"]:
            if (lap["distance"] == self.interval_length_meters) and (int(lap["lap_index"]) != 1) and (int(lap["lap_index"]) != len(self.activity["laps"])):
                #counters for logic
                self.interval_lap_count+=1
                self.next_rec = True
                #extract generic activity properties
                self.row = self.extract_generic_activity_properties()
                #NOTE: proxy to get location. Gotten via the location of one of the segments - If no segments, then null
                location_proxy = self.get_proxy_location()
                self.row["location"] = "%s, %s (%s)" %(location_proxy[0],location_proxy[1],location_proxy[2])
                #extract specific lap properties
                self.row["lap"], self.row["distance"], self.row["seconds"], self.row["elevation_gain_interval"] = self.interval_lap_count, lap["distance"], lap["elapsed_time"], lap["total_elevation_gain"]
                if self.activity["has_heartrate"] == True:
                    self.row["average_heartrate"], self.row["maximum_heartrate"] = lap["average_heartrate"], lap["max_heartrate"]
                
            elif self.next_rec == True:
                self.row = self.extract_recovery_properties(lap)
                self.next_rec = False
                #append self.row to df only after information about recovery has been gathered
                self.df = self.df._append(self.row, ignore_index=True)
                self.row = {} #reset row
        return self.df
    

    def get_interval_instance_of_type_multiple_1000(self):
        #create a copy in case we discard activity in the process
        copy_df = self.df.copy(deep=True)
        next_interval, distance, seconds, elevation_gain_interval,heart_rate, current_max_heart_rate = 0,0,0,0,0,0
        first_recovery = True
        self.interval_lap_count+=1
        consecutive_short = 0 
        #loop over laps
        for lap in self.activity["laps"]:
            #discard if other type of intervals
            if lap["distance"] == 1000:
                consecutive_short+=1
            if lap["distance"] == 1000:
                consecutive_short=0
            if consecutive_short>2: 
                return copy_df
            #check if the lap is different from 1000m
            if (lap["distance"] != 1000) and (next_interval==0):
            # this will make sure that we are either 
                # in a recovery lap
                if self.next_rec == True:
                    #if it is the first recovery lap, extract info about recovery time and store properties
                    if first_recovery == True:
                        first_recovery = False
                        recovery_time = lap["elapsed_time"]
                        next_interval = self.interval_length_meters/1000 #how many of the next laps are intervals
                        self.row = self.extract_recovery_properties(lap)
                        self.df = self.df._append(self.row, ignore_index=True)
                        lap_index_next_interval = lap["lap_index"]

                    #if it is a short interval different from the recovery ones, then break the code (not append last row)
                    elif recovery_time != lap["elapsed_time"]:
                        return self.df
                    #if it is a normal recovery, just do this as usually
                    else:
                        self.row = self.extract_recovery_properties(lap)
                        next_interval = self.interval_length_meters/1000 #how many of the next laps are intervals
                        self.df = self.df._append(self.row, ignore_index=True)
                        lap_index_next_interval = lap["lap_index"]

                    #next one is for sure not a recovery
                    self.next_rec = False


                # cooling down (last lap)
                elif int(lap["lap_index"]) == len(self.activity["laps"]):
                    continue
                # a lap potentially previous to starting interval
                else:
                    next_interval = self.interval_length_meters/1000 #how many of the next laps are intervals
                    lap_index_next_interval = lap["lap_index"]
            #if it is a lap of 1000m and the next interval is positive
            elif (lap["distance"] == 1000) and (next_interval>0):
                #starting interval row
                if (next_interval == self.interval_length_meters/1000) and (lap_index_next_interval == lap["lap_index"]-1):
                    #extract generic activity properties
                    self.row = self.extract_generic_activity_properties()
                    location_proxy = self.get_proxy_location()
                    self.row["location"] = "%s, %s (%s)" %(location_proxy[0],location_proxy[1],location_proxy[2])
                    self.row["lap"] = self.interval_lap_count
                elif (next_interval == self.interval_length_meters/1000) and (lap_index_next_interval != lap["lap_index"]-1):
                    continue
                                        
                #extract specific lap properties - in this case, we append them to lists, to make averages later
                #totals to be stored as totals
                distance += lap["distance"]
                seconds += lap["elapsed_time"]
                elevation_gain_interval+= lap["total_elevation_gain"]
                next_interval-=1
                #heart rate to be manipulated
                if self.activity["has_heartrate"] == True:
                    heart_rate += lap["average_heartrate"]
                    if lap["max_heartrate"] > current_max_heart_rate:
                        current_max_heart_rate = lap["max_heartrate"]

                if next_interval == 0:
                    self.interval_lap_count += 1
                    self.next_rec = True #if last step of the interval, then next lap is recovery
                    #extract stats from previous rows
                    self.row["distance"], self.row["seconds"], self.row["elevation_gain_interval"] = distance, seconds, elevation_gain_interval
                    self.row["average_heartrate"] = (heart_rate)/(self.interval_length_meters/1000)
                    self.row["maximum_heartrate"] = current_max_heart_rate
                    #reset values for next interval lap
                    distance, seconds, elevation_gain_interval, heart_rate, current_max_heart_rate=0,0,0,0,0

            #if whole interval not completed (i.e. we are seeking for 3000m and we only completed 2000m), skip activity
            elif (lap["distance"] != 1000) and (next_interval>0):
                #discard activity - not a 1000m multiple interval session
                if self.interval_lap_count == 0:
                    return copy_df
            #if we are in a recovery lap, but the distance is exactly 1000, it means we are talking about other type of intervals! So discard and return df
            elif (lap["distance"] == 1000) and (self.next_rec==True):
                return copy_df
        
        return self.df
    
            
