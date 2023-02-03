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


def blocks(files, size=65536):
    while True:
        b = files.read(size)
        if not b: break
        yield b

def to_array(var1):
    if type(var1) in (float, int):
        return numpy.array([var1])
    if type(var1) == list:
        return numpy.asarray(var1)
    if type(var1) == numpy.ndarray:
        return var1
    else:
        print('Unkown format of input - please provide: list, int, float')