from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

import pandas as pd 
import numpy as np 
import geopandas as gpd 
from shapely.geometry import Point
import shapely.speedups 
shapely.speedups.enable()


def clustered_trip_removal(taxitrips_after_regular_inference, allowable_dops = 2):
        
    """ 
    remove the grouped dops on daily basis 
    
    dependencies 
    ----------
    DBSCAN
    pandas
     
    Parameters
    ----------
    taxitrips_after_regular_inference - filtered trips after purpose imputation based on regularity 
    allowable_dops -  maximum allowable dops for a cluster to keep 
    
    Returns
    -------
    trips without grouped dops on daily basis  
        
    """
    
    # getting the dates and creating a group object to process the analysis day by day 
    dates = taxitrips_after_regular_inference['drop_time'].dt.day.unique()
    taxidata_perday_g = taxitrips_after_regular_inference.groupby(taxitrips_after_regular_inference['drop_time'].dt.day)
    
    possible_home = pd.DataFrame(columns = taxitrips_after_regular_inference.columns)
    taxidata = pd.DataFrame(columns = taxitrips_after_regular_inference.columns)
    
    for day in dates:
        taxidata_perday = taxidata_perday_g.get_group(day)
        X = taxidata_perday[['dropoff_lat','dropoff_long']]
        model = DBSCAN(eps=0.0002, min_samples = allowable_dops) #20m for the eps
        model.fit(X)
        clusterlabels = model.labels_
        taxidata_perday['cluster_no'] = clusterlabels.tolist()
        selected_data = taxidata_perday[taxidata_perday['cluster_no']==-1]
        possible_home = possible_home.append(selected_data)
        taxidata = taxidata.append(taxidata_perday)
    
    return possible_home , taxidata
    

# function to measure the minimum distance to road from DOPs

def min_road_distance_measure(possible_home,colombo_roads):
    
    """ 
    measure the distance for dops from the nearest main road 
    
    dependencies 
    ----------
    shapely 
    geopandas 
     
    Parameters
    ----------
    possible_home - filtered trips after purpose imputation based on regularity 
    colombo_roads - shapefile of main roads for the selected area
    
    Returns
    -------
    minimum distance imputed possible_home df 
        
    """    
    
    for row in possible_home.itertuples():
        
        Point_DOP =  Point(row.dropoff_long, row.dropoff_lat)
        distancelist = np.array([])
        
        for rows in colombo_roads.itertuples():
            
            distance = (Point_DOP.distance(rows.geometry))*10000 # (1 unit = 11.1 meters approximately)
            
            distancelist = np.append(distancelist, distance)
        
        possible_home.loc[row.Index,'road_min_distace'] = np.min(distancelist)
        
    return possible_home


# function to remove the clusters closer to the main road

def distance_based_trip_removal(possible_home, clusters = 10, n_clusters_toremove = 2):
  
    """ 
    measure the distance for dops from the nearest main road 
    
    dependencies 
    ----------
    KMeans from scikitlearn 
    numpy 
    standard scalar 
    
    Parameters
    ----------
    clusters - number of clusters (n)
    n_clusters_toremove - number of clusters to remove based on the distance
    
    Returns
    -------
    minimum distance imputed possible_home df 
        
    """    
    
    cluster_df = pd.DataFrame(possible_home[['road_min_distace']])
    scaler = StandardScaler()
    X = scaler.fit_transform(cluster_df)
    model = KMeans(n_clusters=clusters, random_state=32) 
    model.fit(X)
    clusterlabels = model.predict(X)
    cluster_df['cluster_name'] = clusterlabels.tolist()
                              
    clusters_to_keep = cluster_df.groupby('cluster_name')['road_min_distace'].max().sort_values()[n_clusters_toremove:].index
                        
    possible_home['cluster_labels'] = clusterlabels.tolist()
    possible_home_selected =  possible_home[possible_home['cluster_labels'].isin(clusters_to_keep)] 
                                                        
    return possible_home_selected, possible_home

def poi_existance_removal(possible_home_selected, placesgpd, allowable_distance = 15):
        
    """ 
    remove the dops with closer pois and return the trips attracted to residential places 
    
    dependencies 
    ----------
    shapely - point 
    geopandas 
    
    Parameters
    ----------
    possible_home_selected - output from the function distance_based_trip_removal
    placesgpd - geopandas df of the POIs
    allowable_distance - maximum allowable distance between POI and DOP to remove it 
    
    Returns
    -------
    df with records relating to trips attracted to residential places 
    
    """

    indexestodrop = []
    
    # consider if there are any POIs exist within a radius of 15m, and if so drop it from the dataframe 
    for row in possible_home_selected.itertuples():
        
        DOP = [row.dropoff_lat, row.dropoff_long]
        Point_DOP = Point(DOP[1],DOP[0]) 
        Buffer = Point_DOP.buffer(allowable_distance*0.001/110) ## (110m = 0.001) (##idk about this convertion but it is right)
        mask = placesgpd.within(Buffer) ## filter the data for the required buffer zone 

        places_per_trip = placesgpd.loc[mask] ## Candidate POIs for the DOP 

        if  places_per_trip.shape[0] == 0:
            possible_home_selected.loc[row.Index,'Trip purpose'] = 0 
        
        else:
            indexestodrop.append(row.Index) 
    
    actual_home_selected = possible_home_selected.drop(indexestodrop)
                                
    return actual_home_selected