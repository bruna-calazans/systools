def convert2utm_tp():

    import os
    import geopandas as gpd
    import main.systool.geo as geo

    file_path = os.path.dirname(os.path.abspath(__file__))
    gdf = gpd.read_file(os.path.join(file_path, r'test_databases\test_geo_deg.shp'))

    assert gdf.crs == 'epsg:4326'

    geo.convert2utm(os.path.join(file_path, r'test_databases'), 'test_geo_deg.shp')
    gdf_converted = gpd.read_file(os.path.join(file_path, r'test_databases\utm_test_geo_deg.shp'))

    assert gdf_converted.crs.coordinate_operation.method_name == 'Transverse Mercator'


def convert2degree_tp():

    import os
    import geopandas as gpd
    import main.systool.geo as geo

    file_path = os.path.dirname(os.path.abspath(__file__))
    gdf = gpd.read_file(os.path.join(file_path, r'test_databases\test_geo_utm.shp'))

    assert gdf.crs.coordinate_operation.method_name == 'Transverse Mercator'

    geo.convert2degree(os.path.join(file_path, r'test_databases'), 'test_geo_utm.shp')
    gdf_converted = gpd.read_file(os.path.join(file_path, r'test_databases\degree_test_geo_utm.shp'))

    assert gdf_converted.crs.ellipsoid == 'WGS 84'


def convert_dataframe_tp():

    import os
    import geopandas as gpd
    import main.systool.geo as geo

    file_path = os.path.dirname(os.path.abspath(__file__))
    gdf = gpd.read_file(os.path.join(file_path, r'test_databases\test_geo_deg.shp'))
    gdf['UTMx'] = gdf['geometry'].x
    gdf['UTMy'] = gdf['geometry'].y

    gdf = geo.convert_dataframe(gdf, 'latLon')

    assert 'LAT' in gdf.columns and 'LON' in gdf.columns

    gdf = geo.convert_dataframe(gdf, 'utm')

    assert 'UTMx' in gdf.columns and 'UTMy' in gdf.columns


def calc_dist_euclidean_tp():

    import os
    import geopandas as gpd
    import main.systool.geo as geo

    file_path = os.path.dirname(os.path.abspath(__file__))
    gdf = gpd.read_file(os.path.join(file_path, r'test_databases\test_geo_deg.shp'))

    gdf['dist_euclidean'] = geo.calc_dist_euclidean(gdf, 'long_1', 'long_2', 'lat_1', 'lat_2')

    assert 'dist_euclidean' in gdf.columns


def calc_dist_milepost_tp():

    import os
    import geopandas as gpd
    import main.systool.geo as geo
    from shapely.geometry import mapping

    file_path = os.path.dirname(os.path.abspath(__file__))
    gdf = gpd.read_file(os.path.join(file_path, r'test_databases\test_milepost.shp'))
    gdf['coords'] = gdf['geometry'].apply(lambda x: mapping(x)['coordinates'])
    gdf = gdf.explode('coords')
    gdf['UTMx'] = gdf['coords'].apply(lambda x: x[0])
    gdf['UTMy'] = gdf['coords'].apply(lambda x: x[1])
    gdf = geo.calc_dist_milepost(gdf)

    assert 'dist' in gdf.columns


def calc_dist_orthogonal_tp():

    import os
    import geopandas as gpd
    import main.systool.geo as geo
    from shapely.geometry import mapping

    file_path = os.path.dirname(os.path.abspath(__file__))
    gdf = gpd.read_file(os.path.join(file_path, r'test_databases\test_milepost.shp'))
    gdf['coords'] = gdf['geometry'].apply(lambda x: mapping(x)['coordinates'])
    gdf = gdf.explode('coords')
    gdf['UTMx'] = gdf['coords'].apply(lambda x: x[0])
    gdf['UTMy'] = gdf['coords'].apply(lambda x: x[1])
    gdf = geo.calc_dist_orthogonal(gdf)

    assert 'dist' in gdf.columns and gdf['dist'].sum() == 0


def flat_geom_tp():

    import geopandas as gpd
    import main.systool.geo as geo
    from shapely.geometry import MultiLineString, LineString

    line_1 = LineString([(0, 1), (1, 1), (1, 3)])
    line_2 = LineString([(0, 2), (2, 1), (2, 3)])
    line_3 = LineString([(0, 3), (3, 1), (3, 3)])

    multiline = MultiLineString([line_1, line_2, line_3])

    gdf = gpd.GeoDataFrame({'id': 0, 'geometry': [multiline]})

    gdf = geo.flat_geom(gdf)

    assert gdf['geometry'].geom_type[0] == 'LineString'
