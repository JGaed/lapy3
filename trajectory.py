#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:46:57 2020
@author: Johannes Gäding
"""

import numpy
import pandas
from helper_functions import check_greater

#---------------------------------------------------
# Class for trajectories in .xyz-fileformat.
# Supports variable number of atoms per frame.
#
# Class is iterable and subscriptable by the n-frames
#
# functions:
#
# <xyz_trajectory>.positions()   	-- xyz-atom coords of selected frame - numpy.array(3,N)
# <xyz_trajectory>.atom_types()	    -- atom-types of slected frame - numpy.array(1,N) - floats
#
# porperties:
#
# <xyz_trajectory>.frame		    -- current selected frame - int
# <xyz_trajectory>.n_frames		    -- number of total frames in trajectory - int
# <xyz_trajectory>.atoms_per_frame	-- number of atoms per timestep - list(N)
# <xyz_trajectory>.content		    -- raw content of file as list(str)
#---------------------------------------------------

class xyz_trajectory:
    
    def __init__(self, filepath):
        self.path = filepath
        self.content = self.__file_content()
        self.n_lines = len(self.content)
        self.atoms_per_frame, self.comments = self.__get_traj_properties()
        self.start_line_per_frame = numpy.hstack(([0], numpy.cumsum(numpy.array(self.atoms_per_frame) + 2)[:-1]))
        self.n_frames = len(self.atoms_per_frame)
        self.iteration_started = False
        self.__iter__()

    def __file_content(self):
        with open(self.path) as f:
            contents = f.readlines()
        return contents
    
    def __get_traj_properties(self):
        atoms_per_frame = list()
        comments = list()
        line = 0
        while line < self.n_lines:
            atoms_per_frame.append(int(self.content[line]))
            comments.append(self.content[line+1].split())
            line = numpy.cumsum(numpy.array(atoms_per_frame)+2)[-1]
        return atoms_per_frame, comments

    def positions(self):
        frame = self.content[self.start_line_per_frame[self.frame]+2:self.start_line_per_frame[self.frame]+self.atoms_per_frame[self.frame]+2]
        return numpy.array([line.split() for line in frame])[:,1:4].astype(float)

    def atom_types(self):    
        frame = self.content[self.start_line_per_frame[self.frame]+2:self.start_line_per_frame[self.frame]+self.atoms_per_frame[self.frame]+2]
        return numpy.array([line.split() for line in frame])[:,0].astype(str)
    
    def __iter__(self):
        self.frame = 0
        return self

    def __next__(self):
        if self.frame < self.n_frames-1:
            if self.iteration_started:
                self.frame += 1
            self.iteration_started = True 
            return self
        else:
            raise StopIteration
    def __getitem__(self, x):
        self.frame = x
        return self

#---------------------------------------------------
# Class for trajectories in LAMMPS-dump-fileformat.
# Supports variable number of atoms per frame.
#
# Class is iterable and subscriptable by the n-frames
#
# functions:
#
# <lammpstrj>.data() 		    -- data of the selected frame - numpy.array(M,N); N = number of atoms; M = number of logged properties
# <lammpstrj>.columns()  	    -- columnnames of the logged properties - list(M)
# <lammpstrj>.cell()		    -- pbcs of the selected frame  - list([xlo, xhi], [ylo, yhi], [zlo, zhi])
# <lammpstrj>.df_frame()	    -- pandas DataFrame containg data+columns of selected timestep df(M,N)
#
# porperties:
#
# <lammpstrj>.frame		        -- current selected frame - int
# <lammpstrj>.n_frames		    -- number of total frames in trajectory - int
# <lammpstrj>.atoms_per_frame	-- number of atoms per timestep - list()
# <lammpstrj>.timesteps	        -- timestep of the logged frames - list()
# <lammpstrj>.content		    -- raw content of file as list()
#---------------------------------------------------

class lammpstrj:

    def __init__(self, filepath):
        self.path = filepath
        self.content = self.__file_content()
        self.n_lines = len(self.content)
        self.timesteps, self.atoms_per_frame = self.__get_traj_properties()
        self.start_line_per_frame = numpy.hstack(([0], numpy.cumsum(numpy.array(self.atoms_per_frame) + 9)[:-1]))
        self.n_frames = len(self.atoms_per_frame)
        self.iteration_started = False
        self.current_line = 0
        self.__iter__()
        self.__print()

    def data(self):
        frame = self.content[self.start_line_per_frame[self.frame]+9:self.start_line_per_frame[self.frame]+self.atoms_per_frame[self.frame]+9]
        return numpy.array([line.split() for line in frame]).astype(float)        

    def cell(self):
        frame = self.content[self.start_line_per_frame[self.frame]+5:self.start_line_per_frame[self.frame]+8]
        return numpy.array([i.split() for i in frame]).astype(float).tolist()

    def columns(self):
        frame = self.content[self.start_line_per_frame[self.frame]+8]        
        return frame.split()[2:]  
    
    def df_frame(self):
        return pandas.DataFrame(data=self.data(), columns=self.columns())

    def __file_content(self):
        with open(self.path) as f:
            contents = f.readlines()
        return contents
    
    def read_lines(self, lines_of_interest):
        lines_to_return = list()
        if not check_greater(lines_of_interest, self.current_line):
            self.file.seek(0)
            self.current_line = 0
        for line in self.file:
            print(line)
            if numpy.isin(self.current_line, lines_of_interest):
                lines_to_return.append(line.strip())
            self.current_line +=1
            if self.current_line > numpy.max(lines_of_interest):
                break
        return lines_to_return


    def __get_traj_properties(self):
        timesteps = list()
        atoms_per_frame = list()
        line = 0
        while line < self.n_lines:
            timesteps.append(int(self.content[line+1]))
            atoms_per_frame.append(int(self.content[line+3]))
            line = numpy.cumsum(numpy.array(atoms_per_frame)+9)[-1]
        return timesteps, atoms_per_frame 

    def __print(self):
        print('Loaded LAMMPS trajectory file "{file}" containing {frames} frames.'.format(file=self.path, frames=self.n_frames))

    def __iter__(self):
        self.frame = 0
        return self

    def __next__(self):
        if self.frame < self.n_frames-1:
            if self.iteration_started:
                self.frame += 1
            self.iteration_started = True 
            return self
        else:
            raise StopIteration
    def __getitem__(self, x):
        self.frame = x
        return self

    def __exit__(self):
        self.file.close()


class lammpstrj2:
    def __init__(self, filepath):
        self.path = filepath
        self.file = open(self.path, "r")
        self.current_line = 0

