# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:28:14 2022

@author: bcalazans

Módulo com funções úteis no tratamento de dados tabulados.

"""
# Python Modules
import pandas as pd
import textwrap
from inspect import currentframe

# Systools Modules
import systools.helpers.readWrite as rW


def dataframe2numeric(df, col_dt_preffix=None, col_td_preffix=None):

    """Transform the dataFrame to numeric and time formats..."""

    other_cols = [col for col in df.columns if df[col].dtype != 'datetime64[ns]']
    all_cols = df.columns
    
    # Transform to numeric but keep datetime.
    df[other_cols] = df[other_cols].apply(pd.to_numeric, errors='ignore')
    
    # Select Cols to Convert
    cols_dt = [col for col in all_cols if col.startswith(col_dt_preffix)]
    cols_td = [col for col in all_cols if col.startswith(col_td_preffix)]
    
    # Transform Timedeltas and Datetimes to its format.
    for col in cols_td:
        df[col] = pd.to_timedelta(df[col])

    # Transform in datetime commonly used formats in Brazil.

    time_formats = ["%d/%m/%Y %H:%M:%S",
                    "%d/%m/%Y %H:%M",
                    "%Y/%m/%d %H:%M:%S",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M"]

    for col in cols_dt:
        for time_format in time_formats:
            try:
                df[col] = pd.to_datetime(df[col], format=time_format)
                break
            except ValueError:
                continue

        if df[col].dtype != 'datetime64[ns]':
            df[col] = pd.to_datetime(df[col], infer_datetime_format=True)

    return df


def open_file(path, name=None, expected_cols=None, usa=False, col_td_preffix='gap',  col_dt_preffix='H_', **kwargs):

    """
    Open file as a geopandas.DataFrame.
    Support csv, txt, parquet, excel, shape, dbf and ziped files.

    Parameters
    ----------
    path : string
        Path of the file, may include the file name with extension
        If the file is zipped, pass the path with the zip extension
    name : string, optional
        Name of the file with extension to be open. 
        The default is None. Expects that the name was passed on the path arg
    expected_cols : list, optional
        Import only this cols. The default is None.
    usa : Bool, optional
        If TRUE expects comma separetor and point as decimal indicator. 
        If FALSE expects ; as separetor and comma as decimal indicator.
        The default is False.
    col_dt_preffix: String, optional
        Indicates column name preffix to be converted to datetime.
        The default is 'H_'
    col_td_preffix: String, optional
        BRUNA ESCREVER SIGNIFICADO AQUI
        The default is 'gap'.
    **kwargs : dict
        Any argment for the original read functions from (geo)pandas.

    Returns
    -------
    df : pd.DataFrame or geo.DataFrame
        DataFrame do arquivo lido contendo ou não geometria.

    """
    
    df = rW.load_file(path, name, expected_cols, usa, **kwargs)
         
    # configure formats
    df = dataframe2numeric(df, col_dt_preffix, col_td_preffix)
    print(f'{currentframe().f_code.co_name} {textwrap.shorten(name, width=50):50} {len(df):>9,}')
    return df


# Insert excel parameters if needed, after the "truncate_sheet" parameter.

def save_file(df, path, name='test', usa=False, ext='csv',
              sheet_name='Sheet1', start_row=None, truncate_sheet=False):

    # Salva o arquivo em CSV (default) ou SHP (defalut se tiver geometria).
    # Pode escolher tbm as outras coisas

    # If ext=='excel' :
    # Truncate_sheet.
    # False: append data to existing sheet on the start_row.
    # True: delete sheet and paste data on a new one.
            
    extensions = ['shp', 'csv', 'parquet', 'excel']

    if 'geometry' in df.columns or ext == 'shp':
        rW.save_df_as_shp(df, path, name)
    elif ext == 'csv':
        rW.save_df_as_csv(df, path, name, usa)
    elif ext == 'parquet':
        rW.save_df_as_parquet(df, path, name)
    elif ext == 'excel':
        rW.save_df_as_excel(df, path, name, sheet_name, start_row, truncate_sheet)
    else: 
        raise Exception(f'ext parameter must be one of the following {extensions}')
    print(f'{currentframe().f_code.co_name} {textwrap.shorten(name, width=50):50} {len(df):>9,}')
    return None


def get_col(df, get_cols, from_df, key, key2=None):
    """
    Add cols on df
    param df: data frame to add cols on.
    param get_cols: columns from other data frame you want the info.
    param from_df: data frame that you will look up the info (get_cols).
    param key: key to merge (on parameter from merge method).
    key2: BRUNA ESCREVER SIGNIFICADO AQUI.
    return: df with columns get_cols added.
    """

    if isinstance(key, str):
        key = [key]
    if isinstance(get_cols, str):
        get_cols = [get_cols]
    
    if key2 is not None:
        # If key2 is passed, then the keys are different in each df.
        if isinstance(key2, str):
            key2 = [key2]
        assert len(key) == len(key2), 'key and key2 must be of the same size'
        # Make dummy columns to avoid repetition and get only the desired cols
        for i, col in enumerate(key):
            df['temp'+str(i)] = df[col]
        for i, col in enumerate(key2):
            from_df['temp'+str(i)] = from_df[col]
        key = ['temp'+str(i) for i in range(len(key))]
    
    if isinstance(key, list) and isinstance(get_cols, list):
        cols = key + get_cols
    else:
        raise Exception('KEY and GET_COLS must be string or lists')
    
    # Perform the merge.
    # Using the method not the function since function fails when df is GeoPandas.
    # Assure types.
    from_df[key] = from_df[key].astype(df[key].dtypes)
    ans = df.merge(from_df[cols].drop_duplicates(key), on=key, how='left')
    
    if len(ans) != len(df):
        print(len(ans), len(df))
        raise Exception('Error performing get_col: ON not right')
    
    if key2 is not None:
        # Delete the temporary columns
        ans.drop(columns=key, inplace=True)
        from_df.drop(columns=key, inplace=True) 
    return ans


def get_mask_isin(df, key, base_data):
    if isinstance(key, list):
        new_col = '_'.join(key)
        my_list_series = []
        for k in key:
            my_list_series.append(list(df[k].values))
        df[new_col] = list(zip(*my_list_series))
        mask = df[new_col].isin(base_data)
        del df[new_col]
    else:    
        mask = df[key].isin(base_data)
    return mask


def remove_duplicate_safe(df, cols):
    num = len(df)
    df = df.drop_duplicates(cols)
    diff = num-len(df)
    if diff > 0:
        print('fDuplicates removed from{name:}[{cols:}]{diff:,}{diff/num:,.2f}')
    return df


def flatten_hierarchical_col(col, sep='_'):
    """
    Use after make a groupby operation with agg that cuases a multi level
    --- USAGE: 
        df.columns = df.columns.map(flattenHierarchicalCol)
    """

    if not type(col) is tuple:
        new_col = col
    else:
        new_col = ''
        for leveli, level in enumerate(col):
            if not level == '':
                if not leveli == 0:
                    new_col += sep
                new_col += str(level)
    return new_col


def download():
    # Faz o download automático de dados do IBGE/vários outros
    return None
