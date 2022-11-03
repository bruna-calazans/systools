# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:28:14 2022

@author: bcalazans & MoleDownTheHole (pcardoso)

Módulo com funções úteis no tratamento de dados tabulados.

"""
# Python Modules
import pandas as pd

# Systools Modules
from .utils import readWrite as rW


def dataframe2numeric(df, col_dt_preffix='', col_td_preffix=''):

    """
    Format the DataFrame columns to Numeric and Time Formats.
    Support datetime, timestamp, int and float formats.

    Parameters
    ----------
    df : DataFrame
        DataFrame type variable that has columns who will be converted
        to numeric or time format.

    col_dt_preffix : string, optional
        String type variable that have the prefixes used to show that
        the designated column title that contains it,
        must be converted to datetime type.

    col_td_preffix : string, optional
        String type variable that have the prefixes used to show that
        the designated column title that contains it,
        must be converted to timedelta type.

    Returns
    -------

    df : DataFrame
    DataFrame used in the input, but with the numeric and time columns converted.

    """

    other_cols = [col for col in df.columns if df[col].dtype != 'datetime64[ns]']
    all_cols = df.columns
    
    # Transform to numeric but keep datetime.
    df[other_cols] = df[other_cols].apply(pd.to_numeric, errors='ignore')
    
    # Select Cols to Convert
    if col_dt_preffix != '':

        cols_dt = [col for col in all_cols if str(col).startswith(col_dt_preffix)]

    else:
        cols_dt = []

    if col_td_preffix != '':

        cols_td = [col for col in all_cols if str(col).startswith(col_td_preffix)]

    else:
        cols_td = []
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


def open_file(path, name=None, expected_cols=None, usa=False, col_td_prefix='gap',  col_dt_prefix='H_', **kwargs):

    """
    Open file as a DataFrame.
    Support csv, txt, parquet, excel and shape.

    Parameters
    ----------
    path : string
        Path of the file, may include the file name with extension.
        If the file is zipped, pass the path with the zip extension.

    name : string, optional
        Name of the file with extension to be open.
        Expects that the name was passed on the path arg.

    expected_cols : list, optional
        Import only this cols.
    usa : Bool, optional
        If TRUE expects comma separator and point as decimal indicator.
        If FALSE expects ; as separator and comma as decimal indicator.

    col_dt_prefix: String, optional
        Indicates column name prefix to be converted to datetime.

    col_td_prefix: String, optional
        Indicates column name prefix to be converted to timedelta.

    **kwargs : dict
        Any argument for the original read functions from (geo)pandas.

    Returns
    -------
    df : pd.DataFrame or geo.DataFrame
        DataFrame do arquivo lido contendo ou não geometria.

    """
    
    df = rW.load_file(path, name, expected_cols, usa, **kwargs)
         
    # Configure Formats
    df = dataframe2numeric(df, col_dt_prefix, col_td_prefix)
    return df


# Insert excel parameters if needed, after the "truncate_sheet" parameter.

def save_file(df, path, name='test', usa=False, ext='csv',
              sheet_name='Sheet1', start_row=None, truncate_sheet=False):
    """
    Save DataFrame to an exterior file created and formated based
    on various parameters.
    Support csv, txt, parquet, excel and shape.

    Parameters
    ----------
    df : DataFrame
        DataFrame type variable that has columns who the user
        wants to export.

    path : String
        Path of the file.
        Doesn't need to have the filename and extension included.

    name : String, optional
        File name.
        Doesn't need to have the extension included.

    usa : Boolean, optional
        True -> The exported file uses the american format.
        (Ex: Comma as separator, dot as decimal...)
        False -> The exported file doesn't uses the american format.
        (Ex: Semicolon as separator, comma as decimal...)

    ext : String, optional
        The file extension.
        Must be csv, txt, parquet, excel or shape.

    sheet_name : String, optional
        The file, when saved as an excel file, sheet name.

    start_row : Integer, optional
        The excel file row where the user wants the new data to be inserted.

    truncate_sheet : Boolean, optional
        Remove and recreate the destination sheet of the exported excel file.

    """
            
    extensions = ['shp', 'csv', 'parquet', 'xlsx']

    if 'geometry' in df.columns or ext == 'shp':
        rW.save_df_as_shp(df, path, name)
    elif ext == 'csv':
        rW.save_df_as_csv(df, path, name, usa)
    elif ext == 'parquet':
        rW.save_df_as_parquet(df, path, name)
    elif ext == 'xlsx':
        rW.save_df_as_excel(df, path, name, sheet_name, start_row, truncate_sheet)
    else: 
        raise Exception(f'ext parameter must be one of the following {extensions}')
    return None


def get_col(df, get_cols, from_df, key, key2=None):

    """
    Add columns to an input DataFrame, originated from another DataFrame
    based on a merge correspondence with in common column.

    Parameters
    ----------
    df : DataFrame
        Main input dataframe that will receive the merged columns.

    get_cols : List
        Columns from the other input dataframe you want to merge.

    from_df : DataFrame
        Secondary input dataframe that will be used to get the
        columns to be merged.

    key : String
        Column in main DataFrame used as key to merge the two DataFrames.

    key2 : String, optional
        Column in secondary DataFrame used as key to merge the two DataFrames.

    Returns
    -------
    ans : DataFrame
        Main input DataFrame with the merged columns.

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

    """
    Get a filter mask to be used in a DataFrame based on
    single ou multiple filter.
    (Easier than the usual way)

    Parameters
    ----------
    df : DataFrame
        DataFrame that the user want to create a mask.

    key : String or List
        The column, or columns, that the filter will be applied.

    base_data : List and Tuple
        List filled with tuples that each one represents one filter.

    Returns
    -------
    mask : Series
        A Series of Boolean values that can be used as a mask for
        the input DataFrame.

    """

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

    """
    Remove DataFrame duplicates based on a column,
    or multiple columns, value.

    Parameters
    ----------
    df : DataFrame
        Dataframe that the user want to drop duplicates.

    cols : String or List
        Column or list of columns used as parameter for
        the drop_duplicates function.

    Returns
    -------
    df : DataFrame
        DataFrame without the duplicates in cols parameter.

    """

    num = len(df)
    df = df.drop_duplicates(cols)
    diff = num-len(df)
    if diff > 0:
        print(f'Duplicates removed from [{cols:}]{diff:,}{diff/num:,.2f}')
    return df


def flatten_hierarchical_col(col, sep='_'):

    """
    Turn multi-index column names into single index
    separated by '_'.

    Parameters
    ----------

    col : Multi-Index Column Title
        Multi-Index column that will be replaced for a single_index column.
    sep : String, optional
        Separator for the single_index column name.

    Returns
    -------
    new_col : Single_Index Column Title
        Multi_Index column title passed in the parameters, but flattened
        as no hierarchical title.

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

# Faz o download automático de dados do IBGE/vários outros.

# def download():
    # return None
