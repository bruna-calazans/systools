# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 17:01:40 2023

@author: bcalazans

Esboço de arquivo de teste antes de subir systool para pypi
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join('..')))
from main.systool import data
import pandas as pd

txt = data.open_file(r'examples_databases\open_file\si-log-2020.txt', kwargs = {'encoding' : 'latin1'})
assert txt.shape == (14181, 16), 'Erro in data.open_file'

'''
data.dataframe2numeric(df, col_dt_preffix='', col_td_preffix='')
data.save_file(df, path, name='test', usa=False, ext='csv',
              sheet_name='Sheet1', start_row=None, truncate_sheet=False,
              kwargs={})
data.get_col(df, get_cols, from_df, key, key2=None)
data.get_mask_isin(df, key, base_data)
data.remove_duplicate_safe(df, cols)
data.flatten_hierarchical_col(col, sep='_')
'''