import systool.helpers.charts as ch
import systool.helpers.maps as mp
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import numpy as np
import geopandas as gpd


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
        ax2.legend(loc='lower center')
        ch.hide_grid(ax2)
        ch.bars_auto_label(ax2, what_ticks, per, decimal=0, pos_above=True)

    if legend_control == '%V':

        per = True

        ax1.patch.set_facecolor('none')
        if ax2 is not None:
            ax2.patch.set_facecolor('none')
        ax_aux = ax1.twinx()

        what.plot.bar(stacked=True, ax=ax_aux, legend=legenda)
        if xlabel is not None:
            ax1.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
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
        if ax2 is not None:
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
         col_size=3, coords=None, dir_col='DIR', col_zns=None, heat=None):

    """
    Function used to plot maps based on multiple inputed GeoDataFrames.

        Parameters
        ----------
        shapes: list
            List of the GeoDataFrames that the user wants to plot.
        path: str
            String value with the file output path for the maps
            ploted using this function.
        title: str
            Title of the map.
        subtitle: str
            Subtitle of the map.
        col_lin: str
            String value responsible for doing two different things:
            1 - Determinate what color you want the linestrings to be.
            or
            2 - Determinate what GeoDataFrame column you want to be used
        dir2dashed: bool
            Boolean value to indicate if the analized linestrings have
            multiple directions.
        col_pts: str
            String value responsible for doing two different things:
            1 - Determinate what color you want the points to be.
            or
            2 - Determinate what GeoDataFrame column you want to be used
                as categoric values for the points.
        col_size: int or str
            Determinate the size of the point ploted values.
        coords: list
            List of GeoDataFrame columns responsible to share the coordinates
            of the point data that are going to be ploted if there wasn't any
            geometry column.
        dir_col: str
            String value with the name of the column that have the direction
            data.
        col_zns: str
            String value responsible for doing two different things:
            1 - Determinate what color you want the polygons to be.
            or
            2 - Determinate what GeoDataFrame column you want to be used
                as categoric values for the polygons.
        heat: str
            String value with the seaborn color pallete used for
            cloropletic maps. It will create a cloropletic zone
            classification

        Returns
        -------

        fig : Matplotlib figure type.
            Figure containing the ploted map.

    """

    lines_plot = gpd.GeoDataFrame(columns=['geometry'])
    points_plot = gpd.GeoDataFrame(columns=['geometry'])
    zones_plot = gpd.GeoDataFrame(columns=['geometry'])
    lines = gpd.GeoDataFrame(columns=['geometry'])
    points = gpd.GeoDataFrame(columns=['geometry'])
    zones = gpd.GeoDataFrame(columns=['geometry'])

    for shape in shapes:

        if 'geometry' not in shape.columns:
            points_gdf = mp.config_crs(shape, coords)
            points_gdf = points_gdf.set_crs('epsg:4674', allow_override=True)
            points_plot = points_plot.append(points_gdf, ignore_index=True)
            points_plot = gpd.GeoDataFrame(points_plot['geometry'])
            shape_type = points_plot['geometry'].geom_type.to_list()
            shape_type = list(set(shape_type))
            shape = points_gdf.copy()

        if 'geometry' in shape.columns:
            shape_type = shape['geometry'].geom_type.to_list()
            shape_type = list(set(shape_type))

            if len(shape_type) == 1:
                if shape_type[0] == 'Point' or shape_type[0] == 'MultiPoint':
                    points_gdf = shape
                    points_gdf = points_gdf.set_crs('epsg:4674', allow_override=True)
                    points_plot = points.append(points_gdf, ignore_index=True)
                    points_plot = gpd.GeoDataFrame(points_plot['geometry'])
                elif shape_type[0] == 'Polygon' or shape_type[0] == 'MultiPolygon':
                    zones_gdf = shape
                    zones_gdf = zones_gdf.set_crs('epsg:4674', allow_override=True)
                    zones_plot = zones_plot.append(zones_gdf, ignore_index=True)
                    zones_plot = gpd.GeoDataFrame(zones_plot['geometry'])
                elif shape_type[0] == 'LineString' or shape_type[0] == 'MultiLineString':
                    lines_gdf = shape
                    lines_gdf = lines_gdf.set_crs('epsg:4674', allow_override=True)
                    lines_plot = lines_plot.append(lines_gdf, ignore_index=True)
                    lines_plot = gpd.GeoDataFrame(lines_plot['geometry'])

            elif len(shape_type) == 2:
                if shape_type[0] == 'Point' and shape_type[0] == 'MultiPoint':
                    points_gdf = shape
                    points_gdf = points_gdf.set_crs('epsg:4674', allow_override=True)
                    points_plot = points.append(points_gdf, ignore_index=True)
                    points_plot = gpd.GeoDataFrame(points_plot['geometry'])
                elif shape_type[0] == 'Polygon' and shape_type[0] == 'MultiPolygon':
                    zones_gdf = shape
                    zones_gdf = zones_gdf.set_crs('epsg:4674', allow_override=True)
                    zones_plot = zones_plot.append(zones_gdf, ignore_index=True)
                    zones_plot = gpd.GeoDataFrame(zones_plot['geometry'])
                elif shape_type[0] == 'LineString' and shape_type[0] == 'MultiLineString':
                    lines_gdf = shape
                    lines_gdf = lines_gdf.set_crs('epsg:4674', allow_override=True)
                    lines_plot = lines_plot.append(lines_gdf, ignore_index=True)
                    lines_plot = gpd.GeoDataFrame(lines_plot['geometry'])

            elif len(shape_type) > 2:
                lines_gdf = shape[(shape['geometry'].geom_type ==
                                   'LineString') | (shape['geometry'] == 'MultiLineString')].copy()
                points_gdf = shape[(shape['geometry'].geom_type == 'Point') |
                                   (shape['geometry'] == 'MultiPoint')].copy()
                zones_gdf = shape[(shape['geometry'].geom_type == 'Polygon') |
                                  (shape['geometry'] == 'MultiPolygon')].copy()
                points_gdf = points_gdf.set_crs('epsg:4674', allow_override=True)
                zones_gdf = zones_gdf.set_crs('epsg:4674', allow_override=True)
                lines_gdf = lines_gdf.set_crs('epsg:4674', allow_override=True)
                points_plot = points.append(points_gdf, ignore_index=True)
                points_plot = gpd.GeoDataFrame(points_plot['geometry'])
                lines_plot = lines_plot.append(lines_gdf, ignore_index=True)
                lines_plot = gpd.GeoDataFrame(lines_plot['geometry'])
                zones_plot = zones_plot.append(zones_gdf, ignore_index=True)
                zones_plot = gpd.GeoDataFrame(zones_plot['geometry'])

        if dir2dashed and dir_col in shape.columns:
            lines_plot = lines_plot.merge(shape[['geometry', dir_col]], how='right', left_on='geometry',
                                          right_on='geometry')
            lines = lines.append(lines_plot)
        if col_pts in shape.columns and (shape_type[0] == 'Point' or shape_type[0] == 'MultiPoint'):
            points_plot = points_plot.merge(shape[['geometry', col_pts]], how='right', left_on='geometry',
                                            right_on='geometry')
            points = points.append(points_plot)
        if col_lin in shape.columns and (shape_type[0] == 'LineString' or shape_type[0] == 'MultiLineString'):
            lines_plot = lines_plot.merge(shape[['geometry', col_lin]], how='right', left_on='geometry',
                                          right_on='geometry')
            lines = lines.append(lines_plot)
        if col_zns in shape.columns and (shape_type[0] == 'Polygon' or shape_type[0] == 'MultiPolygon'):
            zones_plot = zones_plot.merge(shape[['geometry', col_zns]], how='right', left_on='geometry',
                                          right_on='geometry')
            zones = zones.append(zones_plot)
        if col_size in shape.columns and (shape_type[0] == 'Point' or shape_type[0] == 'MultiPoint'):
            points_plot = points_plot.merge(shape[['geometry', col_size]], how='right', left_on='geometry',
                                            right_on='geometry')
            points = points.append(points_plot)

    points.dropna(inplace=True)
    lines.dropna(inplace=True)
    zones.dropna(inplace=True)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    fig.suptitle(f'{title}\n{subtitle}', fontsize=20, ha='left', va='center', x=0.125, y=0.95, **{'fontname': 'Lato'})
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.add_artist(ScaleBar(1))

    if lines is not None and len(lines) > 0:
        lines, col_lin, color = mp.group_data(lines, col_lin, 'Rotas')
        if dir2dashed and dir_col in lines.columns:
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
                              linewidth=1, linestyle='-' * (i + 1),
                              aspect='equal')
                else:
                    data.plot(color=color,
                              label=ctype,
                              ax=ax,
                              linewidth=1, linestyle='-' * (i + 1),
                              aspect='equal')

    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)
    x, y, arrow_length = 0.1, 0.15, 0.1
    ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center', fontsize=20,
                xycoords=ax.transAxes)

    def corresp(var):
        if var == 1:
            return 3
        if var == 2:
            return 20
        if var == 3:
            return 40
        if var == 4:
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
                                   markersize=corresp(size),
                                   aspect='equal')
                    else:
                        data2.plot(color=color,
                                   label=ctype + labels[size - 1],
                                   ax=ax,
                                   markersize=corresp(size),
                                   aspect='equal')
            else:
                if color is None:
                    data.plot(color=color_attrs[ctype],
                              label=ctype,
                              ax=ax, zorder=10,
                              markersize=col_size,
                              aspect='equal')
                else:
                    data.plot(color=color,
                              label=ctype,
                              ax=ax, zorder=10,
                              markersize=col_size,
                              aspect='equal')

    if zones is not None and len(zones) > 0:
        zones, col_zns, color = mp.group_data(zones, col_zns, 'Zonas')
        color_attrs = mp.get_colors(zones, col_zns, heat_def=heat)
        for ctype, data in zones.groupby(col_zns):
            if color is None:
                data.plot(color=color_attrs[ctype],
                          label=ctype,
                          ax=ax,
                          alpha=0.3, edgecolor='black',
                          aspect='equal')
            else:
                data.plot(color=color,
                          label=ctype,
                          ax=ax,
                          alpha=0.3, edgecolor='black',
                          aspect='equal')

    ax.legend(fontsize=6, loc='upper left')  # attention
    plt.axis('equal')
    if path is not None:
        file_name = os.path.join(path, 'chart_' + title + '.png')
        plt.savefig(file_name, dpi=300, bbox_inches='tight',
                    pad_inches=0.5, facecolor='#F2F2F2')

    return fig


def plot_sidemap(map_left, map_right, file_name=None):

    """
    Function that is responsible for plot two early created maps side by side.

        Parameters
        ----------
        map_left: Matplotlib figure type
            Figure of the map you want to be plotted on the left
            side of the new figure.
        map_right: Matplotlib figure type
            Figure of the map you want to be plotted on the right
            side of the new figure.
        file_name: str
            String value with the path and file name of the exported
            new figure.

        Returns
        -------

        fig : Matplotlib figure type.
            Figure containing the two ploted maps, side by side.

    """

    dpi = 300

    backend = mpl.get_backend()
    mpl.use('agg')

    c1 = map_left.canvas
    c2 = map_right.canvas
    c1.draw()
    c2.draw()

    a1 = np.array(c1.buffer_rgba())
    a2 = np.array(c2.buffer_rgba())
    a = np.hstack((a1, a2))

    mpl.use(backend)
    fig, ax = plt.subplots(figsize=(6000 / dpi, 3000 / dpi), dpi=dpi)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_axis_off()
    ax.matshow(a)
    if file_name is not None:
        plt.savefig(file_name, dpi=300, bbox_inches='tight',
                    pad_inches=0.7, facecolor='#F2F2F2')

    return fig
