import pandas as pd 
import numpy as np 
import math
from Functions.linear_distance import qick_distance


def baysean_inference_ln(candidate_pois, lat, long, drop_time, huanggrid):
    
    """ 
    inferring the purpose of a trip given the candidate pois, timestamped DOP and temporal impact for the purposes
    based on the bayesian model that uses pois ratings for the attractiveness factor 
    
    dependencies 
    ----------
    pandas 
    candidate POI df 
    hunaggrid df 
    
    Parameters
    ----------
    lat, long -  cordinates of the drop off point (DOP)
    drop_time -  timestamp of the DOP
    candidate_pois - df for the selected candidate POIs for the DOP
    huanggrid - grid for the temporal impact for purposes. 
    
    Returns
    -------
    inferred trip purpose for the trip as a string 
    
    """    

    day = drop_time.day_of_week # select the required part of the HuangGrid for the DOP day 
    
    if day == 6:
           HuangGrid = huanggrid[huanggrid['Day']== 'sun'] 
    elif day == 5:
           HuangGrid = huanggrid[huanggrid['Day']== 'sat']    
    else:
           HuangGrid = huanggrid[huanggrid['Day']== 'week']
    
    candidate_pois['no_of_ratings'].fillna(0, inplace = True)
    
    # calculate the numerators of the bayesian probabilities    
    for row in candidate_pois.itertuples():
        
        gravity_value = math.log(row.no_of_ratings + math.e) ## take the log e for the no of ratings as the gravity value 
        Huangvalue = HuangGrid[HuangGrid.index.hour == drop_time.hour][row.purpose].values[0]
        distance = qick_distance(lat, long, row.lat, row.lng) 
        candidate_pois.loc[row.Index,'bayes_upper'] = (gravity_value/(distance)**1.5)*(Huangvalue)
    
    # purpose assignment 

    # assignment of "NA" for all the purpose expecting to change in future 
    trip_purpose = 'NA'
    
    # inferring the purpose based on the bayesian method 
    for row in candidate_pois.itertuples():
        bayes_down = candidate_pois['bayes_upper'].sum()

        if bayes_down != 0:
            candidate_pois['bayes2015'] =  candidate_pois['bayes_upper']/bayes_down
            maxvalue = candidate_pois['bayes2015'].max()
            
            #check the multiple purpose assignment 
            if (candidate_pois['bayes2015'] == maxvalue).sum() > 1: 
                trip_purpose = 'multiple' 
            else:
                trip_purpose = candidate_pois[candidate_pois['bayes2015'] == maxvalue]['purpose']      
        
        else:
            trip_purpose = 'NA'
            
    return trip_purpose