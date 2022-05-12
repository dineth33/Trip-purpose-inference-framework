from math import cos, sqrt ## source: STACKOVERFLOW

def qick_distance(Lat1, Long1, Lat2, Long2):

    """ 
    calculates the harvesine distance between two cordinates 
    
    dependencies 
    ----------
    math
     
    Parameters
    ----------
    Lat1, Long1 - cordinates of point 1 
    Lat2, Long2 -  cordinates of point 2 
    
    Returns
    -------
    harvesine distance between the two points  
    
    """
    
    x = Lat2 - Lat1
    y = (Long2 - Long1) * cos((Lat2 + Lat1)*0.00872664626)  
    
    return 111.319 * sqrt(x*x + y*y)*1000