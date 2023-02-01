#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Johannes Gäding
"""

import pickle
import bz2

# Load any compressed pickle file
def decompress_pickle(file):
    data = bz2.BZ2File(file, 'rb')
    data = pickle.load(data)
    return data
    
def compressed_pickle(title, data):
    with bz2.BZ2File(title + '.pbz2', 'w') as f:
        pickle.dump(data, f)

# loads and returns a pickled objects
def loosen(file):
    pikd = open(file, 'rb')
    data = pickle.load(pikd, encoding='latin1')
    pikd.close()
    return data

# Saves the "data" with the "title" and adds the .pickle
def full_pickle(title, data):
    pikd = open(title + '.pickle', 'wb')
    pickle.dump(data, pikd)
    pikd.close()  
   
