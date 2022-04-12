# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:28:14 2022

@author: bcalazans

Módulo com funções úteis no tratamento de dados tabulados

"""
# python modules
import os
import pandas as pd
import textwrap

from inspect import currentframe, stack

# systools modules
import helpers.readWrite as rw

def dataframe2numeric(df, col_dt_preffix=None, col_td_preffix=None):
    """Transform the dataFrame to numeric and time formats"""
    time_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
    other_cols = [col for col in df.columns if df[col].dtype != 'datetime64[ns]']
    all_cols = df.columns
    
    # transform for numeric but keep datetime
    df[other_cols] = df[other_cols].apply(pd.to_numeric, errors='ignore')
    
    # select cols to convert       
    cols_dt = [col for col in all_cols if col.startswith(col_dt_preffix)]
    cols_td = [col for col in all_cols if col.startswith(col_td_preffix)]
    
    ### Transform timedeltas and datetimes to its format
    for col in cols_td:
        df[col] = pd.to_timedelta(df[col])
        
    ### Transform in datetime ussumes commonly used formats in Brasil
    # TODO melhorar esse código, está muito feio
    for col in cols_dt:
        try: df[col] = pd.to_datetime(df[col], format="%d/%m/%Y %H:%M:%S")        
        except:
            try: df[col] = pd.to_datetime(df[col], format="%d/%m/%Y %H:%M")
            except:
                try: df[col] = pd.to_datetime(df[col], format="%Y/%m/%d %H:%M:%S")
                except:
                    try: df[col] = pd.to_datetime(df[col], format="%Y-%m-%d %H:%M:%S")
                    except:
                        try: df[col] = pd.to_datetime(df[col], format="%Y-%m-%d %H:%M")
                        except:
                            df[col] = pd.to_datetime(df[col], infer_datetime_format=True)

    return df


def open_file(path, name=None, expected_cols=None, USA=False, col_td_preffix='gap',  col_dt_preffix='H_', **kwargs):
    '''
    Open file as a (geo)pandas.DataFrame
    Support csv, txt, parquet, excel, shape, dbf and ziped files

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
    USA : Bool, optional
        If TRUE expects comma separetor and point as decimal indicator. 
        If FALSE expects ; as separetor and comma as decimal indicator.
        The default is False.
    col_dt_preffix: String, optional
        Indicates column name preffix to be converted to datetime
        The default is 'H_'
    **kwargs : dict
        Any argment for the original read functions from (geo)pandas.

    Returns
    -------
    df : pd.DataFrame or geo.DataFrame
        DataFrame do arquivo lido contendo ou não geometria.

    '''    
    
    df = rw.load_file(path, name, expected_cols, USA, **kwargs)
         
    # configure formats
    df = dataframe2numeric(df, col_dt_preffix, col_td_preffix)
    print(f'{currentframe().f_code.co_name} {textwrap.shorten(name, width=50):50} {len(df):>9,}')
    return df


def save_file(df, path, name='test', USA=False, info=True, ext='csv',
              sheet_name='Sheet1', startrow=None, truncate_sheet=False, # excel parameters
              **kwargs):
    #salva o arquivo em CSV (default) ou SHP (defalut se tiver geometria). 
    #Pode escolher tbm as outras coisas
    # If ext=='excel' : 
        # truncate_sheet 
            #= False: append data to existing sheet on the startrow
            #= True: delete sheet and paste data on a new one
            
    extensions = ['shp','csv','parquet','excel']
    # Standard keywords to save a dataframe, can be overwriten by kwargs
    keywords = {'index': None,
                'float_format': '%.6f', 
                'date_format': '%d/%m/%Y %H:%M:%S'}
    kwargs = {**keywords, **kwargs}
    
    if 'geometry' in df.columns or ext=='shp':
        rw.save_df_as_shp(df, path, name)
    elif ext=='csv':
        rw.save_df_as_csv(df, path, name, USA, kwargs)
    elif ext=='parquet':
        rw.save_df_as_parquet(df, path, name, kwargs)
    elif ext=='excel':        
        rw.save_df_as_excel(df, path, name, sheet_name, startrow, truncate_sheet, kwargs)
    else: 
        raise Exception (f'ext parameter must be one of the following {extensions}')
    print(f'{currentframe().f_code.co_name} {textwrap.shorten(name, width=50):50} {len(df):>9,}')
    return


def get_col(df, get_cols, from_df, key, key2=None):
    """
    Add cols on df
    :param df: data frame to add cols on
    :param get_cols: columns from other data frame you want the info
    :param from_df: data frame that you will look up the info (get_cols)
    :param key: key to merge (on parameter from merge method)
    :return: df with columns get_cols added
    """

    if isinstance(key, str): key = [key]
    if isinstance(get_cols, str): get_cols = [get_cols]
    
    if key2 is not None:
        # if key2 is passed, then the keys are different in each df.         
        if isinstance(key2, str): key2 = [key2]
        assert len(key) == len(key2), 'key and key2 must be of the same size'
        # make dummy columns to avoid repetition and get only the desired cols
        for i, col in enumerate(key): df['temp'+str(i)] = df[col]
        for i, col in enumerate(key2): from_df['temp'+str(i)] = from_df[col]
        key = ['temp'+str(i) for i in range(len(key))]
    
    if isinstance(key, list) and isinstance(get_cols, list):
        cols = key + get_cols
    else:
        raise Exception('KEY and GET_COLS must be string or lists')
    
    # perform the merge
    # using the method not the function since function fails when df is geoPandas
    from_df[key] = from_df[key].astype(df[key].dtypes) #assure types
    ans = df.merge(from_df[cols].drop_duplicates(key), on=key, how='left')
    
    if len(ans) != len(df):
        print(len(ans), len(df))
        raise Exception('Error performing get_col: ON not right')
    
    if key2 is not None:
        # delete the temporary columns
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
    
def remove_duplicate_safe(df, cols, name='data'):
    num = len(df)
    df = df.drop_duplicates(cols)
    diff = num-len(df)
    if diff > 0:
        print('fDuplicates removed from{name:}[{cols:}]{diff:,}{diff/num:,.2f}')
    return df


def flattenHierarchicalCol(col, sep ='_'):
    '''Use after make a groupby operation with agg that cuases a multi level
    --- USAGE: 
        df.columns = df.columns.map(flattenHierarchicalCol)
    '''

    if not type(col) is tuple: new_col=col
    else:
        new_col = ''
        for leveli,level in enumerate(col):
            if not level == '':
                if not leveli == 0:
                    new_col += sep
                new_col += str(level)
    return new_col

def download():
    #faz o download automático de dados do IBGE/vários outros
    return