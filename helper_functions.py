#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:46:57 2020
@author: Johannes Gäding
"""

import numpy
import pandas

def check_greater(lst, val):
    if type(lst) != list:
        lst2 = list()
        if type(lst)==int:
            lst2.append(lst)
        if type(lst)==float:
            lst2.append(lst)
        if type(lst)==numpy.ndarray:
            lst2 = lst.tolist()
        lst = lst2
    return not any(x < val for x in lst)