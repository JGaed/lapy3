#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:46:57 2020

@author: Johannes Gäding
"""

import numpy

#---------------------- Benni Smooth ------------------------------------------  
def smooth(x, lookahead=21, window='flat', pol_order=2):
    """ Glaettung der Funktion

    Parameter
    __________
    y           ... Eingabevektor
    lookahead   ... Bereich [lookahead/2 ... Zahl ... l/2] aus dem der Mittelwerte gebildet wird
    window      ... Auswahl der Window-Function (flat, Savgol, hamming, bartlett, blackman, hanning, kaiser,...)
    pol_order   ... Polynomgrad der Aproximationsfunktion für den SavGol filter
    """

    # Korrektur der Eingaben
    if lookahead % 2 == 0:
        lookahead += 1

    aa = int(lookahead // 2)

    # Faltung des Vektors fuer Mittelwerte am Vektorrand
    s = numpy.r_[x[lookahead - 1:0:-1], x, x[-2:-lookahead - 1:-1]]

    # Auswahl des Mittelwertalgorythmus
    if window == 'SavGol':
        y = savgol_filter(x, lookahead, pol_order)
    else:
        if window == 'flat':  # moving average
            w = numpy.ones(lookahead, 'd')
        else:
            w = eval('ws.' + window + '(lookahead)')

        # Bildung Mittelwerte
        y = numpy.convolve(w / w.sum(), s, mode='valid')

        # Beschneiden des Vektors
        y = y[aa:-aa]

    return y
 
def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def reduce_memory_usage(df, verbose=True):
    numerics = ["int8", "int16", "int32", "int64", "float16", "float32", "float64"]
    start_mem = df.memory_usage().sum() / 1024
    for col in df.columns:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == "int":
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if (
                    c_min > np.finfo(np.float16).min
                    and c_max < np.finfo(np.float16).max
                ):
                    df[col] = df[col].astype(np.float16)
                elif (
                    c_min > np.finfo(np.float32).min
                    and c_max < np.finfo(np.float32).max
                ):
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
    end_mem = df.memory_usage().sum() / 1024
    if verbose:
        print(
            "Mem. usage decreased to {:.2f} Mb ({:.1f}% reduction)".format(
                end_mem, 100 * (start_mem - end_mem) / start_mem
            )
        )
    return df
