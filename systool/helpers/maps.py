import geopandas as gpd
from shapely.geometry import Point
import seaborn as sns


def config_crs(geo, aux=None):
    if not (isinstance(geo, gpd.GeoDataFrame)):
        geometry = [Point(xy) for xy in zip(geo[aux[0]], geo[aux[1]])]
        geo = geo.drop(aux, axis=1)
        geo = gpd.GeoDataFrame(geo, geometry=geometry)
    geo.crs = "+proj=utm +zone=23 +ellps=WGS84 +datum=WGS84 +units=m +no_defs +south"
    geo = geo.to_crs("EPSG:3857")  # need to convert to WEB-UTM
    return geo


def get_main_frame(frames):
    # an order to have a main frame
    for f in frames:
        if f is not None and len(f) > 0:
            return f


def group_data(geo, col, label):
    if col is None:
        # creates a temp col with a unique atribute
        col = 'temp'
        geo[col] = label
    return geo, col


def get_colors(geo, col, pal='hls'):
    keys = list(geo[col].unique())
    values = sns.color_palette(pal, n_colors=len(keys))
    # values = sns.color_palette("Paired", n_colors=len(keys))
    color_attrs = dict(zip(keys, values))
    return color_attrs
