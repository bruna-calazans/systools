# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 16:58:55 2018

@author: bcalazans

Miscellaneous file with functions that can/may be used by everyone
"""
import os
import numbers
import pandas as pd
import numpy as np
import myAux.readWrite as rw

from openpyxl import load_workbook
from inspect import currentframe, stack
from datetime import datetime

glob_count = 0
def test():
    print("hi from misc!")    
    return 1


# %% Basic functions
class CColor:
   """
   \033[       Escape code, this is always the same
   1           Style, (0 or 1 = normal, 3 = italic, 4 = underline)
   32          Text colour, 32 for white.
   40m         Background colour, 40 is for black.
   """
   BLUE = '\033[0;34;m'
   GREEN = '\033[0;32;m'
   RED = '\033[0;31;m'     

   ITALIC = '\033[3;30;m'         
   UNDERLINE = '\033[4;30;m'    
   ENDC = '\033[0;30;m'

   LAND = '#F9F6D8'
   SEA = '#DCF0FA'
   BORDER = '#696969'
   STREET = '#C0C0C0'
   

def log(list2print, option=None):
    """
    Prints an information on the prompt based on the list of items
    :param list2print: list of items to print
    :param option: configure stringformat adding style to it
    :return: nothing

    ------ Examples of use
    from numpy.random import randint
    df = pd.DataFrame(randint(0,3,size=(10, 4)), columns=list('ABCD'))
    mask = df.A >= 1
    df['C'] = df['D']/0.5
    log(['Testring my log', 123456789, 9.876])
    log(['Column A >= 1', mask])
    log(['Sum colum B', df.B.sum()])
    log(['Sum colum C', df.C.sum()])
    log(['Dropping A >= 1', mask], option='w')
    log([df])
    """
    # check passed parameters
    options = ['w', 'warning', 'u', 'underline', 'i', 'italic',
                'blue', 'green', 'per', None]
    assert option in options, 'Param' + option + 'unknown.\n ' \
                              'Options are: ' + options

    # build string to print
    my_str = ''
    msg_error = 'log function not structured to print that'
    for pos, val in enumerate(list2print[:]):
        if isinstance(val, pd.core.frame.DataFrame):
            #header = list(val.columns)
            #header = '\t'.join(str(e) for e in header)
            #print(CColor.UNDERLINE + header + CColor.ENDC)
            #print(val.to_csv(sep='\t', index=False, header=None))
            print(val)
            list2print.remove(val)
        elif isinstance(val, str): my_str = my_str + '{:<60}  '
        elif isinstance(val, list): 
            my_str = my_str + '{:<60}  '
            list2print[pos] = ', '.join(val)
        elif isinstance(val, numbers.Integral): my_str = my_str + '{:>12,}  '
        elif isinstance(val, numbers.Real):
            if option == 'per':
                my_str = my_str + '{:>10.2%}  '
            else:
                my_str = my_str + '{:>10,.2}  '
        elif isinstance(val, pd.core.series.Series):
            # if is a boolean mask, will compute the percentual
            if pd.api.types.is_bool_dtype(val):
                if len(val) > 0 :tot = len(val)
                else: tot = 1
                list2print[pos] = val.sum()
                list2print = list2print[:pos+1] \
                             + [(val.sum()/tot)] \
                             + list2print[pos+1:]
                my_str = my_str + '{:>12,}  {:>10.2%}  '
            else:
                raise Exception(msg_error)
        else:
            raise Exception(msg_error)

    # add style to string
    if option in ['w', 'warning']: my_str = CColor.RED + my_str 
    elif option in ['u', 'underline']: my_str = CColor.UNDERLINE + my_str 
    elif option in ['i', 'italic']: my_str = CColor.ITALIC + my_str 
    elif option in ['blue']: my_str = CColor.BLUE + my_str 
    elif option in ['green']: my_str = CColor.GREEN + my_str
    elif option == 'per': pass
    elif option is None: pass
    else:
        raise Exception('Forgot to add option here!')

    # print and return        
    my_str = my_str + CColor.ENDC   
    print(my_str.format(*list2print))
    # Call me to log on file
    #print_on_file(my_str.format(*list2print))
    return


def print_on_file(text):
    name_file = str(datetime.today().date()) + '.log'
    with open(name_file, "a") as f:
        f.write(text)
    return


def my_print(str2print):
    global glob_count
    glob_count = 1 # do smth to count how many functions was called out
    str2print = '\t'*glob_count + str2print
    print(str2print)
    return



def generate_od_pairs(list_of_ids):
    ''' Generates all combinations and return a data frame'''
    from itertools import product
    pairs = list(product(list_of_ids, repeat=2))
    return pd.DataFrame(pairs, columns=['ORG','DST'])
