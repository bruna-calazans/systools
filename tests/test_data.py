# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:53:10 2022

@author: bcalazans
"""
from .context import systools as st

def test_file_was_readen():
    st.data.read()
    return