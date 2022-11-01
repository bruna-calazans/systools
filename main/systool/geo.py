# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:28:14 2022

@author: bcalazans & MoleDownTheHole (pcardoso)

Módulo com funções úteis no tratamento de dados tabulados.

"""
# Python Modules
import os
import geopandas as gpd
import pandas as pd
import numpy as np
from pyproj import Proj
from shapely.geometry import LineString, Point

# Systool Modules
from .utils import flatt_geom as fg


def calc_dist_euclidean(df, x1, x2, y1, y2):

    """
    Calculate the euclidean distances between given coordinates of a Dataframe.

    Parameters
    ----------

    df: DataFrame
        DataFrame containing the coordinates.
    x1: String
        Dataframe column name with the
        origin Longitudes.
    x2: String
        Dataframe column name with the
        destination Longitudes.
    y1: String
        Dataframe column name with the
        origin Latitudes.
    y2: String
        Dataframe column name with the
        destination Latitudes.

    Returns
    -------

    result: Float
            Result of the euclidean distance.

    """

    df[x1] = pd.to_numeric(df[x1], errors='coerce')
    df[x2] = pd.to_numeric(df[x2], errors='coerce')
    df[y1] = pd.to_numeric(df[y1], errors='coerce')
    df[y2] = pd.to_numeric(df[y2], errors='coerce')

    result = np.sqrt((df[x1] - df[x2]) ** 2 + (df[y1] - df[y2]) ** 2)

    return result


def calc_dist_milepost(gdf, mask=None, x='UTMx', y='UTMy', new_col='dist'):

    """

    Calculates the distance in meters of a point along the line (milepost).
    ATTENTION! GeoDataFrame must be projected in mercator.

    Parameters
    ----------
    gdf: GeoDataFrame
         GeoDataFrame containing the geographical data
         that the milepost are going to be calculated.
    mask: Pandas Bool Series
          Pandas Bool Series to mask the given
          GeoDataFrame.
    x: String
       Longitude column name.
    y: LineString
       Latitude column name.
    new_col: String
             Column name for the calculated milepost.

    Returns
    -------

    gdf: GeoDataFrame
         Inputted GeoDataFrame now with the mileposts
         distance column.

    """

    if mask is None:
        mask = np.ones(len(gdf), dtype=bool)

    # uses pe as a auxiliary column
    gdf['pe'] = [Point(xx, yy) for xx, yy in zip(gdf[x], gdf[y])]

    # calculate the distance as a new column
    gdf.loc[mask, new_col] = (gpd.GeoSeries(gdf.loc[mask, 'geometry']).project(gpd.GeoSeries(gdf.loc[mask, 'pe'])))
    gdf.loc[~mask, new_col] = None  # garantees if colum already existed to erase

    gdf = gdf.drop('pe', 1)

    return gdf


def calc_dist_orthogonal(df, mask=None, x='UTMx', y='UTMy', new_col='dist'):

    """
    Calculates the minimum distance between a coord (x,y) and a line 
    (i.e., the orthogonal projection).
    ATTENTION ! geo.DataFrame must be projected in mercator.

    Parameters
    ----------
    df: GeoDataFrame
        GeoDataFrame containing the geometry
        lines and all coordinates.
    mask: Pandas Bool Series
          Pandas Bool Series to mask the given
          GeoDataFrame.
    x: String
       Longitude column name.
    y: LineString
       Latitude column name.
    new_col: String
             Column name for the calculated milepost.

    Returns
    -------

    gdf: GeoDataFrame
         Inputted GeoDataFrame now with the mileposts
         distance column.

    """

    # TODO check the CRS of the dataframe using geopandas to see if it is in UTM
    # if not, reproject it for UTM and TELL THE USER that the answer was reprojected

    if mask is None:
        mask = np.ones(len(df), dtype=bool)

    # uses pe as a auxiliary column

    df['pe'] = [Point(xx, yy) for xx, yy in zip(df[x], df[y])]

    # calculate the distance as a new columns

    df.loc[mask, new_col] = (gpd.GeoSeries(df.loc[mask, 'geometry']).distance(gpd.GeoSeries(df.loc[mask, 'pe'])))

    gdf = df.drop('pe', 1)

    return gdf


# TODO - entender prq isso não está com a atualização do geopandas
# ajustar para geopandas novo q pedro já fez no MovePass

def convert2utm(path, file, utm_zone=23, set_south=True):

    """
    Converts a given shapefile to UTM.
    Saves the file converted in the same path with utm_ as prefix name.

    Parameters
    ----------
    path: String
          Path containing the file to be open
          without the file name and extension.
    file: String
          File name with extension.
    utm_zone: Int
              UTM Zone code.
    set_south: Bool
               True if located in southern hemisphere,
               False if located in northern hemisphere.

    """

    shp = gpd.read_file(os.path.join(path, file))
    my_string = "+proj=utm +zone=" + str(utm_zone) + " +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

    if set_south:

        my_string = my_string + ' +south'

    if shp.crs is None:
        shp.crs = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

    shp = shp.to_crs(my_string)
    shp.to_file(driver='ESRI Shapefile',
                filename=os.path.join(path, 'utm_' + file))
    return


def convert2degree(path, file):

    """
    Converts a given shapefile to degrees, i.e. Lat and Long.
    Saves the file converted in the same path with degree_ as prefix name.

    Parameters
    ----------
    path: String
          Path containing the file to be open
          without the file name and extension.
    file: String
          File name with extension.

    """

    shp = gpd.read_file(os.path.join(path, file))
    my_string = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

    shp.to_crs(my_string)
    shp.to_file(driver='ESRI Shapefile',
                filename=os.path.join(path, 'degree_' + file))

    return


def convert_dataframe(df, convert_to, utm=['UTMx', 'UTMy'], lat_lon=['LAT', 'LON'],
                     utm_zone=23, set_south=True):
    """
    Convert columns of DataFrame from/to degrees/UTM.

    Parameters
    ----------
    df: DataFrame
        DataFrame containing the columns
        that are going to be converted.
    convert_to: String
                Text value with the convertion type.
                Must be 'latLon' or 'UTM'
    utm: List
         Names for the Longitude and Latitude columns
         in UTM that are going to be converted.
    lat_lon: List
             Names for the Longitude and Latitude columns
             in Degrees that are going to be converted.
    utm_zone: Int
              UTM Zone code.
    set_south: Bool
               True if located in southern hemisphere,
               False if located in northern hemisphere.

    Returns
    -------

    df: DataFrame
        Inputted GeoDataFrame now with the mileposts
        distance column.

    """

    my_string = "+proj=utm +zone=" + str(utm_zone) + " +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

    if set_south:
        my_string = my_string + ' +south'
    my_proj = Proj(my_string)
    
    if convert_to == 'latLon':
        lon, lat = my_proj(df[utm[0]].values, df[utm[1]].values, inverse=True)
        for c in utm:
            del df[c]
        df[lat_lon[0]] = lat
        df[lat_lon[1]] = lon
    elif convert_to == 'utm':
        x, y = my_proj(df[lat_lon[1]].values, df[lat_lon[0]].values, inverse=False)
        for c in lat_lon:
            del df[c]
        df[utm[0]] = x
        df[utm[1]] = y
    else:
        raise Exception('convertTo must be ["latLon" or "utm"]')
    return df


def flat_geom(geo):

    """
    Flatten GeoDataFrame geometries.
    Ex: All MultiLineStrings become LineStrings.

    Parameters
    ----------
    geo: GeoDataFrame
         GeoDataFrame with the geometries
         that are going to be flatten.

    Returns
    -------
    geo: GeoDataFrame
         GeoDataFrame with flatten geometries

    """

    geo['x'] = geo.apply(fg.getCoords, geom_col="geometry", coord_type="x", axis=1)
    geo['y'] = geo.apply(fg.getCoords, geom_col="geometry", coord_type="y", axis=1)
    
    geo.x = geo.apply(lambda row: [x for x in row['x'] if ~np.isnan(x)], axis=1)
    geo.y = geo.apply(lambda row: [y for y in row['y'] if ~np.isnan(y)], axis=1)
    
    geo['geometry'] = geo.apply(lambda row: LineString([Point(xy) for xy in zip(row.x, row.y)]), axis=1)

    return geo
