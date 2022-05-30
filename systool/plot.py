import systool.helpers.charts as ch
import systool.helpers.maps as mp
import os
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString


def hist(what, bins=5, lwl=float('-inf'), upl=float('inf'),
         legenda=None, xlabel=None, subtitle='', title='', report_nan=True,
         comentario='', source='', legend_control='%V'):

    """
    Plot a cute histogram based on the source data the user provide.

        Parameters
        ----------
        what: DataFrame or Series
            The data that the user want to be the histogram base.
        bins: integer
            Integer number that represent the number of requisited
            bins that the user want to be in the histogram.
        lwl: float
            Float number to represent the lower limit.
        upl: float
            Float number to represent the upper limit.
        legenda: str
            String value that represents the title of the plot
            legend.
        xlabel: str
            String value responsible for the xlabel title.
        subtitle: str
            String value responsible for the graph subtitle.
        title: str
            String value responsible for the graph title.
        report_nan: bool
            Boolean value responsible to represent if the user
            want or not the column reporting the number of NaN
            values.
        comentario: str
            String value responsible to plot a comment it the bottom
            of the graph.
        source: str
            String value that indicates the source of the data.
        legend_control: str
            String value that indicates the type of graph axis and
            labels displayed.
            V - For just values.
            % - For just percentages.
            V% - For values as labels and percentages as axis.
            %V - For percentages as labels and values as axis.

        Returns
        -------

        fig : Matplotlib figure type.
            Figure containing the results os the histogram plot.

        """

    source = source

    what = ch.check_what(what)
    what_ticks = what.copy()

    fig, ax1, ax2 = ch.create_figure(str(title), str(subtitle), report_nan, source=source, comentario=comentario)

    cols_ref = list(what.columns)
    what, flag_lw, flag_up = ch.clip2plot(what, ch.make_bins(bins, what), lwl, upl)
    bins = ch.make_bins(bins, what)

    stat = ch.get_null_stat(what, legenda)
    what = ch.get_what2plot(what, bins)
    what, legenda = ch.redef_cols(what, cols_ref, legenda)

    if report_nan:
        per = True
        stat.plot.bar(stacked=True, ax=ax2, legend=True,
                      color=['#1C1C1C', '#E6E6E6'])
        ax2.set_xticklabels(stat.index, rotation=0)
        ax2.legend(bbox_to_anchor=(0.326, 1))
        ch.hide_grid(ax2)
        ch.bars_auto_label(ax2, what_ticks, per, decimal=0, pos_above=True)

    if legend_control == '%V':

        per = True

        ax1.patch.set_facecolor('none')
        ax2.patch.set_facecolor('none')
        ax_aux = ax1.twinx()

        what.plot.bar(stacked=True, ax=ax_aux, legend=legenda)
        if xlabel is not None:
            ax_aux.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
        ch.hide_grid(ax1)
        ch.bars_auto_label(ax_aux, what_ticks, per, decimal=1, pos_above=not legenda)

        ax_aux.set_ylabel('N° Ocorrências', rotation=0)
        ax_aux.yaxis.set_label_coords(1, 1.06)
        ax_aux.patch.set_facecolor('none')
        ticks = list(ax_aux.get_yticks())
        new_ticks = [tick * what_ticks.shape[0] for tick in ticks]
        ax_ticks = ax1.twinx()
        ax_ticks.set_yticks(new_ticks)

        ax_ticks.grid(color='grey', linestyle='-', linewidth=0.5)
        ax_ticks.set_zorder(ax_ticks.get_zorder() - 1)
        ax_ticks.set_yticklabels(['{:,.0f}'.format(tick) for tick in new_ticks], color='grey')
        ch.hide_grid(ax_aux)

    elif legend_control == '%':

        per = True

        what.plot.bar(stacked=True, ax=ax1, legend=legenda)
        if xlabel is not None:
            ax1.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
        ch.hide_grid(ax1)
        ch.bars_auto_label(ax1, what_ticks, per, decimal=1, pos_above=not legenda)

    elif legend_control == 'V':
        per = False
        what.plot.bar(stacked=True, ax=ax1, legend=legenda)
        if xlabel is not None:
            ax1.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
        ch.hide_grid(ax1)
        ch.bars_auto_label(ax1, what_ticks, per, decimal=1, pos_above=not legenda)

    elif legend_control == 'V%':

        per = False

        ax1.patch.set_facecolor('none')
        ax2.patch.set_facecolor('none')
        ax_aux = ax1.twinx()

        what.plot.bar(stacked=True, ax=ax_aux, legend=legenda)
        if xlabel is not None:
            ax_aux.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
        ch.hide_grid(ax1)
        ch.bars_auto_label(ax_aux, what_ticks, per, decimal=1, pos_above=not legenda)

        ax_aux.set_ylabel('N° Ocorrências', rotation=0)
        ax_aux.yaxis.set_label_coords(1, 1.06)
        ax_aux.patch.set_facecolor('none')

        ax_aux.grid(color='grey', linestyle='-', linewidth=0.5)
        ax_aux.set_zorder(ax_aux.get_zorder() - 1)
        ax_aux.set_yticklabels(['{:.2f}%'.format(tick * 100) for tick in list(ax_aux.get_yticks())], color='grey')

    if bins[1] - bins[0] == 1:
        ch.adjust_xlabel(ax1, bins[:-1], flag_lw, flag_up)
    else:
        ch.adjust_xlabel(ax1, bins, flag_lw, flag_up)
    
    return fig


def mapa(shapes, path=None, title='', subtitle='', col_lin=None, dir2dashed=False, col_pts=None,
         col_size=3, coords=['UTMx', 'UTMy'], dir_col='DIR', join_pts=None, col_zns=None):

    """
    plota um mapa magicamente
   •	pensar em como adapatar para ter mapa lado a lado tbm automaticamente
   •	Adapatar para ser feito com matplot OU plotly

    Returns
    -------
    fig: objeto do matplotlib ou plotly

    """

    lines = gpd.GeoDataFrame(columns=['geometry'])
    points = gpd.GeoDataFrame(columns=['geometry'])
    zones = gpd.GeoDataFrame(columns=['geometry'])

    for shape in shapes:

        if 'geometry' not in shape.columns:
            points_gdf = mp.config_crs(shape, coords)
            points['geometry'] = points['geometry'].append(points_gdf['geometry'])

        shape_type = shape['geometry'].geom_type.to_list()
        shape_type = list(set(shape_type))

        if len(shape_type) == 1:
            if shape_type[0] == 'Point' or shape_type[0] == 'MultiPoint':
                points_gdf = shape
                points['geometry'] = points['geometry'].append(points_gdf['geometry'])
            elif shape_type[0] == 'Polygon' or shape_type[0] == 'MultiPolygon':
                zones_gdf = shape
                zones['geometry'] = zones['geometry'].append(zones_gdf['geometry'])
            elif shape_type[0] == 'LineString' or shape_type[0] == 'MultiLineString':
                lines_gdf = shape
                if dir2dashed and dir_col in shape.columns:
                    lines['geometry'] = lines['geometry'].append(lines_gdf['geometry'])
                else:
                    lines['geometry'] = lines['geometry'].append(lines_gdf['geometry'])

        elif len(shape_type) == 2:
            if shape_type[0] == 'Point' and shape_type[0] == 'MultiPoint':
                points_gdf = shape
                points['geometry'] = points['geometry'].append(points_gdf['geometry'])
            elif shape_type[0] == 'Polygon' and shape_type[0] == 'MultiPolygon':
                zones_gdf = shape
                zones['geometry'] = zones['geometry'].append(zones_gdf['geometry'])
            elif shape_type[0] == 'LineString' and shape_type[0] == 'MultiLineString':
                lines_gdf = shape
                if dir2dashed and dir_col in shape.columns:
                    lines['geometry'] = lines['geometry'].append(lines_gdf['geometry'])
                else:
                    lines['geometry'] = lines['geometry'].append(lines_gdf['geometry'])

        elif len(shape_type) > 2:
            lines_gdf = shape[(shape['geometry'].geom_type ==
                               'LineString') | (shape['geometry'] == 'MultiLineString')].copy()
            points_gdf = shape[(shape['geometry'].geom_type == 'Point') | (shape['geometry'] == 'MultiPoint')].copy()
            zones_gdf = shape[(shape['geometry'].geom_type == 'Polygon') | (shape['geometry'] == 'MultiPolygon')].copy()
            points['geometry'] = points['geometry'].append(points_gdf['geometry'])
            if dir2dashed and dir_col in shape.columns:
                lines['geometry'] = lines['geometry'].append(lines_gdf['geometry'])
            else:
                lines['geometry'] = lines['geometry'].append(lines_gdf['geometry'])
            zones['geometry'] = zones['geometry'].append(zones_gdf['geometry'])

        if dir2dashed and dir_col in shape.columns:
            lines = lines.merge(shape[['geometry', dir_col]], how='right', left_on='geometry', right_on='geometry')
        if col_pts in shape.columns and (shape_type[0] == 'Point' or shape_type[0] == 'MultiPoint'):
            points = points.merge(shape[['geometry', col_pts]], how='right', left_on='geometry', right_on='geometry')
        if col_lin in shape.columns and (shape_type[0] == 'LineString' or shape_type[0] == 'MultiLineString'):
            lines = lines.merge(shape[['geometry', col_lin]], how='right', left_on='geometry', right_on='geometry')
        if col_zns in shape.columns and (shape_type[0] == 'Polygon' or shape_type[0] == 'MultiPolygon'):
            zones = zones.merge(shape[['geometry', col_zns]], how='right', left_on='geometry', right_on='geometry')

    if join_pts is not None:
        points2line = points.groupby(join_pts)['geometry'].apply(lambda x: LineString(x.tolist()))
        points2line = gpd.GeoDataFrame(points2line, geometry='geometry')
        zoom = lines['geometry'].append(points2line['geometry'])
        zoom.crs = lines.crs

    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    fig.suptitle(f'{title}\n{subtitle}', fontsize=20, ha='left', va='center', x=0.125, y=0.95, **{'fontname': 'Lato'})
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.add_artist(ScaleBar(1))

    if lines is not None and len(lines) > 0:
        lines, col_lin, color = mp.group_data(lines, col_lin, 'Rotas')
        if dir2dashed and 'DIR' in lines.columns:
            lines1 = lines.loc[lines[dir_col] == 1, :]
            lines2 = lines.loc[lines[dir_col] == 2, :]
            lines2plot = [lines1, lines2]
        else:
            lines2plot = [lines]

        for i, geo in enumerate(lines2plot):
            color_attrs = mp.get_colors(geo, col_lin)
            for ctype, data in geo.groupby(col_lin):
                if color is None:
                    data.plot(color=color_attrs[ctype],
                              label=ctype,
                              ax=ax,
                              linewidth=1, linestyle='-' * (i + 1))
                else:
                    data.plot(color=color,
                              label=ctype,
                              ax=ax,
                              linewidth=1, linestyle='-' * (i + 1))

    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)
    x, y, arrow_length = 0.1, 0.15, 0.1
    ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center', fontsize=20,
                xycoords=ax.transAxes)

    def corresp(x):
        if x == 1:
            return 3
        if x == 2:
            return 20
        if x == 3:
            return 40
        if x == 4:
            return 100
        else:
            return 0

    if points is not None and len(points) > 0:
        points, col_pts, color = mp.group_data(points, col_pts, 'POIs')
        color_attrs = mp.get_colors(points, col_pts)

        labels = [0, 200, 400, 800]
        labels = [round(x) for x in labels]

        if isinstance(col_size, str):
            points['size'] = np.digitize(points[col_size], labels)
            labels = [' : menos q 200', ' : menos q 400', ' : menos q 800', ' : MAIS q 800']

        for ctype, data in points.groupby(col_pts):
            if isinstance(col_size, str):
                for size, data2 in data.groupby('size'):
                    if color is None:
                        data2.plot(color=color_attrs[ctype],
                                   label=ctype + labels[size - 1],
                                   ax=ax,
                                   markersize=corresp(size))
                    else:
                        data2.plot(color=color,
                                   label=ctype + labels[size - 1],
                                   ax=ax,
                                   markersize=corresp(size))
            else:
                if color is None:
                    data.plot(color=color_attrs[ctype],
                              label=ctype,
                              ax=ax, zorder=10,
                              markersize=col_size)
                else:
                    data.plot(color=color,
                              label=ctype,
                              ax=ax, zorder=10,
                              markersize=col_size)

    if zones is not None and len(zones) > 0:
        zones, col_zns, color = mp.group_data(zones, col_zns, 'Zonas')
        color_attrs = mp.get_colors(zones, col_zns)
        for ctype, data in zones.groupby(col_zns):
            if color is None:
                data.plot(color=color_attrs[ctype],
                          label=ctype,
                          ax=ax,
                          alpha=0.1, edgecolor='black')
            else:
                data.plot(color=color,
                          label=ctype,
                          ax=ax,
                          alpha=0.1, edgecolor='black')

    ax.legend(fontsize=6, loc='upper left')  # attention
    plt.axis('equal')
    if path is not None:
        file_name = os.path.join(path, 'chart_' + title + '.png')
        plt.savefig(file_name, dpi=300, bbox_inches='tight',
                    pad_inches=0.5, facecolor='#F2F2F2')

    return fig


gdf1 = gpd.read_file(r'C:\Users\pcardoso\Downloads\test_plotmap\line.shp')
gdf2 = gpd.read_file(r'C:\Users\pcardoso\Downloads\test_plotmap\point.shp')
gdf3 = gpd.read_file(r'C:\Users\pcardoso\Downloads\test_plotmap\polygon.shp')
mapa(shapes=[gdf1, gdf2, gdf3], path=r'C:\Users\pcardoso\Downloads\test_plotmap', dir_col='dir',
     title='banana', subtitle='nanica')
