def dataframe2numeric_tp():
    import os
    import pandas as pd
    from systool import data
    file_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(file_path, r'test_databases\test_dataframe2numeric.csv'))
    if df.shape[1] == 1:
        df = pd.read_csv(os.path.join(file_path, r'test_databases\test_dataframe2numeric.csv'), sep=";")
    else:
        pass
    df = data.dataframe2numeric(df, col_dt_preffix='H_', col_td_preffix='TD_')
    datetime_cols = [col for col in df.columns if col.startswith('H_')]
    timedelta_cols = [col for col in df.columns if col.startswith('TD_')]
    other_cols = [col for col in df.columns if col.find('H_') == -1 and col.find('TD_') == -1]
    datetime = 0
    timedelta = 0
    other = 0
    for col in datetime_cols:
        if str(df[col].dtype) != 'datetime64[ns]':
            continue
        else:
            datetime += 1
    for col in timedelta_cols:
        if str(df[col].dtype) != 'timedelta64[ns]':
            continue
        else:
            timedelta += 1
    for col in other_cols:
        if str(df[col].dtype) != 'int64' and str(df[col].dtype) != 'float64':
            continue
        else:
            other += 1
    assert datetime == 5
    assert timedelta == 3
    assert other == 18


def openfile_tp():
    import os
    from systool import data
    file_path = os.path.dirname(os.path.abspath(__file__))
    df1 = data.open_file(file_path, r'test_databases\test_openfile.csv', usa=True)
    df2 = data.open_file(file_path, r'test_databases\test_openfile.xlsx', usa=True)
    df3 = data.open_file(file_path, r'test_databases\test_openfile.shp', usa=True)
    df4 = data.open_file(file_path, r'test_databases\test_openfile.parquet', usa=True)
    df5 = data.open_file(file_path, r'test_databases\test_openfile.txt', usa=True)
    assert df1.equals(df2)
    assert df2.equals(df4)
    assert df4.equals(df5)
    assert df5.equals(df3.iloc[:, :-1])
    assert str(type(df3)) == "<class 'geopandas.geodataframe.GeoDataFrame'>"


def savefile_tp():
    import os
    import geopandas as gpd
    from systool import data
    file_path = os.path.dirname(os.path.abspath(__file__))
    geodf = gpd.read_file(os.path.join(file_path, r'test_databases\test_openfile.shp'))
    df = geodf.iloc[:, :-1]
    extensions = ['csv', 'parquet', 'xlsx']
    for extension in extensions:
        data.save_file(df, os.path.join(file_path, r'test_databases\\'), ext=extension)
    data.save_file(geodf, os.path.join(file_path, r'test_databases\\'))
    extensions_ver = ['csv', 'parquet', 'xlsx', 'shp']
    vers = []
    for extension in extensions_ver:
        ver = os.path.isfile(os.path.join(file_path, rf'test_databases\test.{extension}'))
        vers.append(ver)

    assert vers[0]
    assert vers[1]
    assert vers[2]
    assert vers[3]


def getcols_tp():
    import os
    import pandas as pd
    from systool import data

    file_path = os.path.dirname(os.path.abspath(__file__))
    right = pd.read_excel(os.path.join(file_path, r'test_databases\test_getcols_right.xlsx'), sheet_name='Sheet1')
    left = pd.read_excel(os.path.join(file_path, r'test_databases\test_getcols_left.xlsx'), sheet_name='Sheet1')
    merged = pd.read_excel(os.path.join(file_path, r'test_databases\test_getcols_merged.xlsx'), sheet_name='Sheet1')

    df = data.get_col(left, ['D', 'E'], right, 'C', 'C')

    assert df.equals(merged)


def getmaskisin_tp():
    import os
    import pandas as pd
    from systool import data

    file_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_excel(os.path.join(file_path, r'test_databases\test_getmaskisin.xlsx'),
                       sheet_name='Sheet1')
    mask1 = data.get_mask_isin(df, ['A', 'B'], [(1000, 1), (1001, 1)])
    mask1 = df[mask1]
    mask2 = df[((df['A'] == 1000) & (df['B'] == 1)) | ((df['A'] == 1001) & (df['B'] == 1))]

    assert mask1.equals(mask2)


def removeduplicatessafe_tp():
    import os
    import pandas as pd
    from systool import data

    file_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_excel(os.path.join(file_path, r'test_databases\test_removeduplicatessafe.xlsx'), sheet_name='Sheet1')
    df = data.remove_duplicate_safe(df, ['A', 'B'])
    df = df.reset_index()
    df = df.drop(columns='index')
    df_expected = pd.read_excel(os.path.join(file_path, r'test_databases\test_removeduplicatessafe_expected.xlsx'),
                                sheet_name='Sheet1')

    assert df.equals(df_expected)


def flattenhierarchicalcol_tp():
    import os
    import pandas as pd
    from systool import data

    file_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_excel(os.path.join(file_path, r'test_databases\test_flattenhierarchical_col.xlsx'),
                       sheet_name='Sheet1')
    df_badge = pd.read_csv(os.path.join(file_path, r'test_databases\test_flattenhierarchical_col_badge.csv'))
    df_badge.index = df_badge['B']
    df_badge.drop(columns=['B'], inplace=True)
    df = df.pivot_table(index='B', columns='A').swaplevel(axis=1).sort_index(1)
    mapper = {}
    for column in df.columns:
        mapper[column] = data.flatten_hierarchical_col(column)
    df.columns = df.columns.map(mapper)

    assert df.equals(df_badge)
