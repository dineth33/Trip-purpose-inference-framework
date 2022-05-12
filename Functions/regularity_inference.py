import numpy as np 
import pandas as pd 
from Functions import linear_distance, bayesian_inference

def return_trip_check (onward_indices, passenger_data, matched_indices):
    
    """ 
    identify the existence of round regular trips and if so, the indices of those
    
    dependencies 
    ----------
    numpy 
    qick_distance function 
     
    Parameters
    ----------
    onward_indices - indices of a clustered and time matches set of regular trips
    passenger_data -  trip df for the selected passenger 
    matched_indices - output of the od_pair_check function 
    
    Returns
    -------
    boolean for return trip existence, arrays of indices for return trips
    
    """       

    round_trip = False 
    return_indices = None 
    
    onwards_drop_lat, onwards_drop_long = passenger_data.loc[onward_indices,'dropoff_lat'].mean(), passenger_data.loc[onward_indices,'dropoff_long'].mean()
    onwards_pick_lat, onwards_pick_long = passenger_data.loc[onward_indices,'pickup_lat'].mean(), passenger_data.loc[onward_indices,'pickup_long'].mean()
        
    for key in matched_indices:
        
        return_drop_lat, return_drop_long = passenger_data.loc[matched_indices[key],'dropoff_lat'].mean(), passenger_data.loc[matched_indices[key],'dropoff_long'].mean()
        return_pick_lat, return_pick_long = passenger_data.loc[matched_indices[key],'pickup_lat'].mean(), passenger_data.loc[matched_indices[key],'pickup_long'].mean()
   
        if (linear_distance.qick_distance(onwards_drop_lat, onwards_drop_long, return_pick_lat, return_pick_long) <= 50) & (linear_distance.qick_distance(onwards_pick_lat, onwards_pick_long, return_drop_lat, return_drop_long) <= 50) :
            
            round_trip = True
            return_indices = matched_indices[key]
            
    return round_trip, return_indices 


def round_trip_purpose_inference(candidate_pois, onward_indices, return_indices,  time_bin_purpose, passenger_data):
    
    """ 
    trip purpose inference based on the regular trips for round trips
    
    dependencies 
    ----------
    numpy 
    bayesian model 
     
    Parameters
    ----------
    onward_indices - indices of a clustered and time matches set of regular trips
    passenger_data -  trip df for the selected passenger 
    candidate_pois - selected POIs around the dop 
    return_indices - output of function return trip check 
    time_bin_purpose - assigned purpose from the matched time bin {1 - work, 2 - educational, 3 - work + education}
    
    Returns
    -------
    trip purpose imputed passenger_data df : {0 - home, 1 - work, 2 - educational}
        
    """
        
    if time_bin_purpose == 1: # work
        passenger_data.loc[onward_indices,'Trip purpose'] = 1 
        passenger_data.loc[return_indices,'Trip purpose'] = 0 
    
    elif time_bin_purpose == 2:
        passenger_data.loc[onward_indices,'Trip purpose'] = 2 
        passenger_data.loc[return_indices,'Trip purpose'] = 0 
    
    elif time_bin_purpose == 3:
        
        # check any educational POI exists 
        if 'education' in  candidate_pois['purpose'].values:
            # bayes inference. 
            trip_purpose  = baysean_inference(candidate_pois, latitude, longitude, drop_time, huanggrid)
        
            if trip_purpose == 'education':
                passenger_data.loc[onward_indices,'Trip purpose'] = 2
                passenger_data.loc[return_indices,'Trip purpose'] = 0    
                
            else:
                passenger_data.loc[onward_indices,'Trip purpose'] = 1 
                passenger_data.loc[return_indices,'Trip purpose'] = 0 
                
        else:
            passenger_data.loc[onward_indices,'Trip purpose'] = 1 
            passenger_data.loc[return_indices,'Trip purpose'] = 0 

          
    return passenger_data


def onward_trip_purpose_inference(candidate_pois, onward_indices, time_bin_purpose, passenger_data):
    
    """ 
    trip purpose inference based on the regular trips for onward trips
    
    dependencies 
    ----------
    numpy 
    bayesian inference model 
     
    Parameters
    ----------
    onward_indices - indices of a clustered and time matches set of regular trips
    passenger_data -  trip df for the selected passenger 
    candidate_pois - selected POIs around the dop 
    time_bin_purpose - {1 - work, 2 - educational, 3 - work + education}
    
    Returns
    -------
    trip purpose imputed passenger_data df : {1 - work, 2 - educational}
        
    """
    
    if time_bin_purpose == 1: # work
        passenger_data.loc[onward_indices,'Trip purpose'] = 1 
      
    elif time_bin_purpose == 2:
        passenger_data.loc[onward_indices,'Trip purpose'] = 2 
        
    elif time_bin_purpose == 3:
       
        # check any educational POI exists 
        if 'education' in  candidate_pois['purpose'].values:
            # bayes inference. 
            trip_purpose  = baysean_inference(candidate_pois, latitude, longitude, drop_time, huanggrid)

            if trip_purpose == 'education':
                passenger_data.loc[onward_indices,'Trip purpose'] = 2 
            else:
                passenger_data.loc[onward_indices,'Trip purpose'] = 1 
        else:
            passenger_data.loc[onward_indices,'Trip purpose'] = 1 
               
    return passenger_data