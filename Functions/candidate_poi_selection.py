import pandas as pd 
import numpy as np 
import geopandas as gpd 
from shapely.geometry import Point


def candidate_poi_selection(placesgpd, lat, long, drop_time, time_df, walking_radius = 100):
        
    """ 
    select the candidate POIs for a given timestamped taxi drop off point 
    
    dependencies 
    ----------
    geopandas 
    geopandas dataframe of the places (POIs), (placesgpd)
    dataframe of places opening times (time_df)
     
    Parameters
    ----------
    lat, long -  cordinates of the drop off point (DOP)
    drop_time -  timestamp of the DOP
    walking_radius - maximum allowable radius for a person to walk once got off from the taxi (defalut - 100m)
    
    Returns
    -------
    geopandas df of the selected candidate POIs
    
    """    
    
    Point_DOP = Point(long,lat) 
    Buffer = Point_DOP.buffer(walking_radius*0.001/110) ## (110m = 0.001) 
    mask = placesgpd.within(Buffer) ## filter the data for the required buffer zone 
    
    selected_places = placesgpd.loc[mask] ## POIs within the radius for the DOP 
    
    DOP_time = float(str(drop_time.hour) + '.' + str(drop_time.minute))
    DOP_day = drop_time.day_of_week
    
    for row in selected_places.itertuples():

        # for saturdays 
        if DOP_day == 5:
            
            # take the opening time by the trip purpose of a POI for the unlabelled POIs. 
            if row.type_1 == 'establishment':
                open_time = time_df.loc[row.purpose,'Open_Time_Sat']    
                close_time = time_df.loc[row.purpose ,'Close_Time_Sat']
                if DOP_time <= open_time or DOP_time >= close_time:
                    selected_places = selected_places.drop(row.Index)  # drop the place if it is not within the defined opening time period 
                    
            # take the opening time by the category for the labelled POIs. 
            else:
                open_time = time_df.loc[row.type_1,'Open_Time_Sat']    
                close_time = time_df.loc[row.type_1 ,'Close_Time_Sat']
                if DOP_time <= open_time or DOP_time >= close_time:
                    selected_places = selected_places.drop(row.Index)  

        # for sundays 
        elif DOP_day == 6:
            if row.type_1 == 'establishment':
                open_time = time_df.loc[row.purpose,'Open_Time_Sun']    
                close_time = time_df.loc[row.purpose,'Close_Time_Sun']
                if DOP_time <= open_time or DOP_time >= close_time:
                    selected_places = selected_places.drop(row.Index) 
            else:
                open_time = time_df.loc[row.type_1,'Open_Time_Sun']    
                close_time = time_df.loc[row.type_1,'Close_Time_Sun']
                if DOP_time <= open_time or DOP_time >= close_time:
                    selected_places = selected_places.drop(row.Index) 
         
        # for weekdays
        else:
            if row.type_1 == 'establishment':
                open_time = time_df.loc[row.purpose,'Open_Time']    
                close_time = time_df.loc[row.purpose,'Close_Time']
                if DOP_time <= open_time or DOP_time >= close_time:
                    selected_places = selected_places.drop(row.Index)  
            else:
                open_time = time_df.loc[row.type_1,'Open_Time']    
                close_time = time_df.loc[row.type_1,'Close_Time']
                if DOP_time <= open_time or DOP_time >= close_time:
                    selected_places = selected_places.drop(row.Index)  
                   
    return selected_places