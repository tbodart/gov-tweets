#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 17:14:16 2021

@author: teresabodart

Creating visualizations

Requires US States shapefile folder to be in current dicrectory
Courtesy of https://hub.arcgis.com/

Requires 'part3_processed_data.csv' to be in current directory

"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import numpy as np

# Processed data from part3_data_process.py
processed_df = pd.read_csv('part3_processed_data.csv')

# US States GeoDataFrame from 
usa = gpd.read_file('./States_shapefile-shp/States_shapefile.shp')

# Merging state sentator's info with GeoDataFrame
geo_df = usa.merge(processed_df, left_on = 'State_Name', right_on = 'location')

# Shifting locations of Hawaii and Alaska to better fit on plot
HI = geo_df.State_Name == "HAWAII"
geo_df[HI] = geo_df[HI].set_geometry(geo_df[HI].translate(56))
AK = geo_df.State_Name == "ALASKA"
geo_df[AK] = geo_df[AK].set_geometry(geo_df[AK].scale(.4,.4,.4).translate(40, -40))

# Scatterplot concering account crated year and total COVID mentions
def gov_scatter(processed):
    plt.figure(1, figsize=(5, 3))
    plt.scatter(x=processed.year_created, y=processed.total_covid_mentions, 
                c='indigo', s=25, marker="D")
    plt.title('Fig. 1: Total Covid Mentions by Twitter Join Year', 
              fontdict={'fontsize': '13', 'fontweight' : '3'})
    plt.xlabel('Year Governor Joined Twitter', 
               fontdict={'fontsize': '10', 'fontweight' : '1'})
    plt.ylabel('Total COVID Mentions Past Seven Days', 
               fontdict={'fontsize': '9', 'fontweight' : '1'})
    plt.xticks(np.arange(min(processed.year_created), max(processed.year_created)+1, 1),
               rotation=45)
    
    return plt.show()

# US State choropleth
def gov_choropleth(geo_DataFrame):
    fig, ax = plt.subplots(1, figsize=(5, 3), facecolor='gainsboro')

    sm = plt.cm.ScalarMappable(cmap='YlGnBu', 
                               norm=plt.Normalize(vmin=0, vmax=1))
    sm.set_array([])
    geo_DataFrame.plot(column = 'proportion_includes_covid', ax = ax, 
                       legend = False, cmap = 'YlGnBu')
    ax.set_title('Fig. 2: Proportion of Tweets Mentioning COVID', 
                 fontdict={'fontsize': '13', 'fontweight' : '3'})
    # legend=True was not creating colorbar, found this workaround from
    # https://dev.to/trossii/creating-a-choropleth-map-with-geopandas-2mg8
    cbar = fig.colorbar(sm, orientation='vertical', aspect=20, shrink=.8)
    ax.axis('off')
    
    return plt.show()

# Functions callable from Jupyter notebook