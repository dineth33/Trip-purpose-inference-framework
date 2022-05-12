import numpy as np 
import pandas as pd 
from sklearn.cluster import DBSCAN
from collections import Counter
from Functions import linear_distance, bayesian_inference


def dbscan_clustering(pickup_data, dropoff_data, min_trips):
        
    """ 
    cluster the origin and destinations of regular users seperately and take the assigned cluster numbers 
    
    dependencies 
    ----------
    numpy 
    pandas 
    
    Parameters
    ----------
    pickup_data -  df with positional data for origin 
    dropoff_data -  df with positional data for destination 
    minimum_days - minimum number of trips for clustering (to measure regularity)
    
    Returns
    -------
    cluster numbers for origin and destination as numpy arrays 
    
    """  
    
    # clustering for origin 
    X1 =  pickup_data
    model1 = DBSCAN(eps=0.001, min_samples = min_trips) # minimum number of trips and maximum distance as 100m as parameters. 
    model1.fit(X1)
    origin_cluster_labels = model1.labels_
    
    # clustering for destination 
    X2 =  dropoff_data
    model2 = DBSCAN(eps=0.001, min_samples = min_trips)
    model2.fit(X2)
    destination_cluster_labels = model2.labels_
    
    return origin_cluster_labels, destination_cluster_labels



def od_pair_check(origin_cluster_labels, destination_cluster_labels, minimum_match):
    
    
    """ 
    evaulating the compatability of clustered origin and destination locations
    
    dependencies 
    ----------
    numpy 
    Counter 
    
    Parameters
    ----------
    origin_cluster_labels -  cluster labels at the origin/pup from the function "dbscan clustering"
    destination_cluster_labels -  cluster labels at the dop from the function "dbscan clustering"
    minimum_match - required trips to consider as a regular trip
    
    Returns
    -------
    dictionary of matching indices for the cluster numbers
    
    """      
 
    matching_indexes = dict()

    for no in np.unique(origin_cluster_labels):  # start with origin cluster numbers 
        if no == -1: # ignore the outliers 
            continue   
        else:
            origin_indexes = np.where(origin_cluster_labels == no)[0]

            dop_cluster_count =  Counter(destination_cluster_labels[np.where(origin_cluster_labels == no)]) # count of cluster numbers at destination cluster numbers parallel to select3ed origin cluster number 
            
            if -1 in dop_cluster_count: del dop_cluster_count[-1]
                
            matching_clusters = [k for k in dop_cluster_count if dop_cluster_count[k] >= minimum_match] # filter the numbers with required minimum matching 

        if len(matching_clusters) == 0: # ignore if there arent any matches 
                continue 

        for idx,value in enumerate(matching_clusters): # loop through matching cluster numbers (avoid possibility of having two destination clusters for one origin cluster)
            destination_indexes = np.where(destination_cluster_labels == value)[0]
            matched_indexes = np.intersect1d(origin_indexes, destination_indexes)
            matching_indexes[value] = matched_indexes
            

    return matching_indexes 
    
    
def time_check(passenger_data, destination_cluster_labels, minium_match,  **time_range):
        
    """ 
    evaluate the compatibility between the defined time bins for regular trip purposes (work and education) and drop off times
    
    dependencies 
    ----------
    numpy 
    Counter 
    
    Parameters
    ----------
    passenger_data -  trip df for the selected passenger 
    destination_cluster_labels -  cluster labels at the dop from the function "dbscan clustering"
    minimum_match - required trips to consider as a regular trip
    **time_range - {work1: 1st time period for work, work2: 2nd time period for work, education: time period for education}
    note: time ranges should be add argument names as 'work1', 'work2', 'education, as lists like [6,10]
    
    Returns
    -------
    dictionary of matching destination cluster number and the assigned time comptability sign 
    return an array for the compatibility with time bins as 0 - non,  1 - work, 2, - education, 3 - work + education
    
    if shape of the output array = 0 - no compatibility, >1 - complex compatibility, 1 - acceptable
    
    """      
     
    regular_purpose = int() # 0 - non,  1 - work, 2 - work + education
    regular_purposes = dict() # assuming if two dop clusters meet the time frame requirements, it will be saved in the dictionary    
    
    for no in np.unique(destination_cluster_labels):
        if no == -1: # ignore the outliers 
            continue   
        else:
            cluster_hours = passenger_data.loc[np.where(destination_cluster_labels == no)]['drop_time'].dt.hour.values # take the hours for the selected dop cluster 
            
            work1_match = ((cluster_hours >= time_range['work1'][0]) & (cluster_hours <= time_range['work1'][1])).sum()
            work2_match = ((cluster_hours >= time_range['work2'][0]) & (cluster_hours <= time_range['work2'][1])).sum()
            education_match = ((cluster_hours >= time_range['education'][0]) & (cluster_hours <= time_range['education'][1])).sum()
            
            if work1_match >= minium_match:
                regular_purpose += 1   # add the defined values for possible regular purposes by passenger
            
            elif work2_match >= minium_match:
                regular_purpose += 1
            
            elif work1_match + work2_match >= minium_match:
                regular_purpose += 1            
            
            if education_match >=  minium_match:
                regular_purpose += 2          

            regular_purposes[no] = regular_purpose

    return regular_purposes


