# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 10:55:13 2018

@author: bcalazans

Funções para calcular distâncias entre:
    (ponto, ponto) : euclidiana
    (ponto, linha) : projeção orthogonal 
    (ponto, linha) : milepost
"""
import sys, os
import geopandas as gpd
import pandas as pd
import numpy as np
import numbers

from pyproj import Proj
from shapely.geometry import LineString, Point

# systools modules
import flatt_geom as fg

#%% CALC DISTANCES
def calc_dist_euclidean(df, x1, x2, y1, y2):
    df[x1] = pd.to_numeric(df[x1],errors='coerce')
    df[x2] = pd.to_numeric(df[x2],errors='coerce')
    df[y1] = pd.to_numeric(df[y1],errors='coerce')
    df[y2] = pd.to_numeric(df[y2],errors='coerce')
    return np.sqrt((df[x1] - df[x2]) ** 2 + (df[y1] - df[y2]) ** 2)


def calc_dist_milepost(df, mask=None, x='UTMx', y='UTMy', new_col='dist'):
    '''Calculates the distance in meters of a point along the line (milepost)
    ATENTION ! geo.DataFrame must be projected in mercator'''
    if mask is None: mask = np.ones(len(df), dtype=bool)
    # uses pe as a auxiliary column
    df['pe'] = [Point(xx, yy) for xx, yy in zip(df[x], df[y])]
    # calculate the distance as a new column
    df.loc[mask, new_col] = (gpd.GeoSeries(df.loc[mask, 'geometry']).project(
        gpd.GeoSeries(df.loc[mask, 'pe'])))
    df.loc[~mask, new_col] = None # garantees if colum already existed to erase
    return df.drop('pe', 1)


def calc_dist_orthogonal(df, mask=None, x='UTMx', y='UTMy',
                                    new_col='dist'):
    """
    Calculates the minimum distance between a coord (x,y) and a line 
    (i.e., the orthogonal projection)
    
    ATENTION ! geo.DataFrame must be projected in mercator
    
    :param df: geodata frame containing the geometry lines and all coordinates
    :param mask:
    :param x: column with coordinate X
    :param y: column with coordiante Y
    :param new_col: new colum for the distance
    :return:
    """
    #TODO check the CRS of the dataframe using geopandas to see if it is in UTM
    # if not, reproject it for UTM and TELL THE USER that the answer was reprojected
    if mask is None: mask = np.ones(len(df), dtype=bool)
    # uses pe as a auxiliary column
    df['pe'] = [Point(xx, yy) for xx, yy in zip(df[x], df[y])]
    # calculate the distance as a new columns
    df.loc[mask, new_col] = (gpd.GeoSeries(df.loc[mask, 'geometry']).distance(
        gpd.GeoSeries(df.loc[mask, 'pe'])))
    return df.drop('pe', 1)


#%% CONVERT GEOMETRIES

# TODO - entender prq isso não está com a atualização do geopandas
# ajustar para geopandas novo q pedro já fez no MovePass
def convert2UTM(PATH, FILE, utmZone=23, setSouth=True):
    '''
    Converts a given shapefile to UTM
    Saves the file converted in the same path with utm_ as prefix name
    :param PATH: path of file to open
    :param FILE: name of file to open
    :param utmZone: zone of the region, exemple: Belo Horizonte = 23
    :param setSouth: bool, true if located in southen hemisfer
    :return: Null
    '''
    shp = gpd.read_file(os.path.join(PATH, FILE))
    myString = "+proj=utm +zone=" + str(utmZone) \
             + " +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

    if setSouth: myString = myString + ' +south'

    if len(shp.crs) <=0: shp.crs =  "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

    shp=shp.to_crs(myString)
    shp.to_file(driver='ESRI Shapefile',
                filename=os.path.join(PATH, 'utm_' + FILE))
    return


def convert2degree(PATH, FILE):
    '''
    Converts a given shapefile to degrees, i.e. Lat and Long
    Saves the file converted in the same path with degree_ as prefix name
    :param PATH: path of file to open
    :param FILE: name of file to open
    :return: Null
    '''
    shp = gpd.read_file(os.path.join(PATH, FILE))
    myString = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

    shp.to_crs(myString)
    shp.to_file(driver='ESRI Shapefile',
                filename=os.path.join(PATH, 'degree_' + FILE))
    return


def convertDataFrame(df, convertTo, utm=['UTMx', 'UTMy'], latLon=['LAT', 'LON'],
                     utmZone=23, setSouth=True):
    ''' Convert columns of df from/to graus/UTM'''
    myString = "+proj=utm +zone=" + str(utmZone) \
             + " +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

    if setSouth: myString = myString + ' +south'
    myProj = Proj(myString)
    
    if convertTo == 'latLon':
        lon, lat = myProj(df[utm[0]].values, df[utm[1]].values, inverse=True)
        for c in utm: del df[c]
        df[latLon[0]] = lat
        df[latLon[1]] = lon
    elif convertTo == 'utm':
        x, y = myProj(df[latLon[1]].values, df[latLon[0]].values, inverse=False)
        for c in latLon: del df[c]
        df[utm[0]] = x
        df[utm[1]] = y
    else:
        raise Exception('convertTo must be ["latLon" or "utm"]')
    return df        

#%% FLATTEN GEOMETRY
def flat_geom(geo):
    '''
    Recebe uma geoPandasDataFrame com geometrias e flatten them
    Ex. todas as multilinestrings viram LineStrings
    
    '''
    geo['x'] = geo.apply(fg.getCoords, geom_col="geometry", coord_type="x", axis=1)
    geo['y'] = geo.apply(fg.getCoords, geom_col="geometry", coord_type="y", axis=1)
    
    geo.x=geo.apply(lambda row: [x for x in row['x'] if ~np.isnan(x)],axis=1)
    geo.y=geo.apply(lambda row: [y for y in row['y'] if ~np.isnan(y)],axis=1)
    
    geo['geometry'] = geo.apply(lambda row: LineString([Point(xy) for xy in zip(row.x,row.y)]),axis=1)
    return geo        