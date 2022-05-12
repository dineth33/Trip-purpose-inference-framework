










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
    