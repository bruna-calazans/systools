def hist_tp():

    import os
    import pandas as pd
    import main.systool.plot as plot

    file_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(file_path, r'test_databases\test_plot.csv'), encoding='latin1', sep=';')
    df = pd.pivot_table(df, values='Nº_boletim', index='tipo_logradouro', aggfunc='count')
    fig = plot.hist(df['Nº_boletim'], title='Número de Acidentes de Tráfego em Belo Horizonte',
                    subtitle='Por Tipo de Logradouro', legenda='Qtd. Acidentes',
                    xlabel='Analized Intervals', source='BhTrans',
                    comentario='Dados retirados do serviços de dados abertos da BhTrans',
                    bins=4, lwl=0, upl=200, report_nan=True)
    fig.savefig(r'test_outputs\plot_tp.png')
    
    assert os.path.exists(r'test_outputs\plot_tp.png')


def mapa_tp():

    import os
    import pandas as pd
    import geopandas as gpd
    import main.systool.plot as plot

    title = 'Linha de Metrô e Terminais de Ônibus'

    file_path = os.path.dirname(os.path.abspath(__file__))
    gdf_metro_lines = gpd.read_file(os.path.join(file_path, r'test_databases\infraurbana_viario_metro.shp'))
    gdf_bus_stations = gpd.read_file(os.path.join(file_path, r'test_databases\ESTACAO_ONIBUS.shp'))
    gdf_bh_regions = gpd.read_file(os.path.join(file_path, r'test_databases\REGIONAL.shp'))
    gdf_metro_station = pd.read_csv(os.path.join(file_path, r'test_databases\ESTACAO_METRO.csv'), sep=';')
    plot.mapa(shapes=[gdf_bh_regions, gdf_bus_stations, gdf_metro_lines, gdf_metro_station],
              coords=['LAT', 'LON'], col_pts='blue', col_lin='Name', col_zns='POPULAÇÃO', heat='Blues',
              title=title, subtitle='Por População Regional', path=file_path + r'\test_outputs',
              col_size='COUNT_FIG', dir2dashed=True, dir_col='dir')

    assert os.path.exists(rf'test_outputs\chart_{title}.png')


def plotsidemap_tp():

    import os
    import pandas as pd
    import geopandas as gpd
    import main.systool.plot as plot

    title = 'Linha de Metrô e Terminais de Ônibus - Sidemap'

    file_path = os.path.dirname(os.path.abspath(__file__))
    gdf_metro_lines = gpd.read_file(os.path.join(file_path, r'test_databases\infraurbana_viario_metro.shp'))
    gdf_bus_stations = gpd.read_file(os.path.join(file_path, r'test_databases\ESTACAO_ONIBUS.shp'))
    gdf_bh_regions = gpd.read_file(os.path.join(file_path, r'test_databases\REGIONAL.shp'))
    gdf_metro_station = pd.read_csv(os.path.join(file_path, r'test_databases\ESTACAO_METRO.csv'), sep=';')
    left = plot.mapa(shapes=[gdf_bh_regions, gdf_bus_stations, gdf_metro_lines, gdf_metro_station],
                     coords=['LAT', 'LON'], col_pts='blue', col_lin='Name', col_zns='POPULAÇÃO', heat='Blues',
                     title=title, subtitle='Por População Regional', col_size='COUNT_FIG', dir2dashed=True,
                     dir_col='dir')
    right = plot.mapa(shapes=[gdf_bh_regions, gdf_bus_stations, gdf_metro_lines, gdf_metro_station],
                      coords=['LAT', 'LON'], col_pts='blue', col_lin='Name', col_zns='POPULAÇÃO', heat='Oranges',
                      title=title, subtitle='Por População Regional', col_size='COUNT_FIG', dir2dashed=True,
                      dir_col='dir')
    plot.plot_sidemap(left, right, os.path.join(file_path, rf'test_outputs\{title}.png'))

    assert os.path.exists(rf'test_outputs\{title}.png')
