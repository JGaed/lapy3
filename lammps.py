#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:46:57 2020

@author: Johannes Gäding
"""

import numpy
import pandas
import scipy

#---------------------------------------------------
# Function to read lammps.log files.
# Returns a dictionary with n_runs, according to the
# number of "run" commands in the lammps-input script.
# To avoid problems with multiple timesteps by 
# using reset_timestep for example.
#---------------------------------------------------

def read_log(log_filename):
    log_file = open(log_filename, 'r')
    lines = log_file.readlines()
    count = 0
    add = 0

    run_log_dict = {}
    run = 0

    for line in lines:
        txt_line = line.strip()
        if len(line.split())!=0:
            if 'Step' in txt_line:
                run_log_dict[run] = list()
                add = 1
                parameters_i = txt_line.split()
                run_log_dict[run].append(txt_line.split())
            if 'Loop' in txt_line:
                add = 0
                run = run + 1
            if add == 1:
                if txt_line.split()[0].isnumeric():
                    run_log_dict[run].append(txt_line.split())

    df_log_dict = {}
    for i in list(run_log_dict.keys()):
        log_i = run_log_dict[i]
        names_i = run_log_dict[i][0]
        data_i = run_log_dict[i][1:]
        df = pandas.DataFrame(data_i, columns=names_i)
        df = df.apply(pandas.to_numeric, errors='coerce')
        df_log_dict[i] = df
    
    log_file.close()
        
    return df_log_dict

# Reads data from LAMMPS of fix ave/time file
def read_ave_time(filename):

    print('Reading file {}'.format(filename))
    df_data = pandas.read_csv(filename)
    df_data.set_axis(['i'], axis = 1, inplace = True)
    df_data = df_data.i.str.split(expand=True)
    header = list(df_data.iloc[0,1:].values)
    header.append('del')
    df_data.set_axis(header, axis = 1, inplace = True)
    df_data = df_data.iloc[1:]
    df_data.reset_index(drop=True, inplace=True)

    df_data = df_data.drop(['del'], axis=1)
    df_data = df_data.apply(pandas.to_numeric)
    print('File processed: {}'.format(filename))

    return df_data

# Reads data from lammps chunk density files
# returns two dataframes: 
# first: whole data
# second: averaged data by all frames
def chunk_dens(filename):
    
    df_data = pandas.read_csv(filename)
    df_data.set_axis(['chunk'], axis = 1, inplace = True)
    df_data = df_data.chunk.str.split(expand=True)
    df_data = df_data.iloc[2:]
    df_data = df_data.drop([4], axis=1)
    
    df_data = df_data.apply(pandas.to_numeric)
    df_data.reset_index(drop=True, inplace=True)
    df_data.set_axis(["chunk", "coord", "Ncount", "dens"], axis = 1, inplace = True)
    
    n_chunks = df_data.iloc[0,1]
    lines = n_chunks+1
    chunk_list = list(range(1, int(lines), 1))
    df_avg = pandas.DataFrame()
    coords = df_data.coord[1:int(lines)].values
    
    df_avg['chunk'] = chunk_list
    df_avg['coord'] = coords
    df_avg['dens'] = numpy.nan
    df_avg['std'] = numpy.nan
    
    for i in chunk_list:
        df_avg.loc[i-1, 'dens'] = numpy.mean(df_data.dens[df_data.chunk==i])
        df_avg.loc[i-1, 'std'] = numpy.std(df_data.dens[df_data.chunk==i])

    return df_data, df_avg

# Reads data from LAMMPS fix ave/chunk file
# Variable number of chunks supported

def read_ave_chunk(filename):
    print('Reading file: {}'.format(filename))
    df_data = pandas.read_csv(filename)
    df_data.set_axis(['i'], axis = 1, inplace = True)
    df_data = df_data.i.str.split(expand=True)
    header = numpy.array(df_data.iloc[2,0:3].values).astype(float)
    column_names = list(df_data.iloc[1,1:].values)
    df_data = df_data.iloc[2:,:-1]
    df_data.reset_index(drop = True, inplace = True)
    df_data.columns = column_names
    df_data = df_data.apply(pandas.to_numeric)
    number_of_chunks = list()
    timesteps = list()
    number_of_chunks.append(int(df_data.iloc[0,1]))
    timesteps.append(int(df_data.iloc[0,0]))
    current_line = 0
    while current_line < len(df_data)-(number_of_chunks[-1]+1):
        current_line = current_line+(number_of_chunks[-1]+1)
        number_of_chunks.append(int(df_data.iloc[current_line,1]))
        timesteps.append(int(df_data.iloc[current_line,0]))
    lines_per_timestep = numpy.array(number_of_chunks)+1
    end_indicies = numpy.cumsum(lines_per_timestep)
    start_indicies = scipy.ndimage.interpolation.shift(end_indicies, 1, cval = 0)
    data_dict = {}
    i = 0
    while i < len(start_indicies):
         data_dict[timesteps[i]]=df_data.iloc[start_indicies[i]+1:end_indicies[i]]
         i = i + 1
    print('File processed: {}'.format(filename))

    return data_dict
