#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:46:57 2020
@author: Johannes Gäding
"""

import numpy
import pandas
import helper_functions
from file_format_settings import lammps_dump as ldump

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
        if not helper_functions.check_greater(lines_of_interest, self.current_line):
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

    def __init__(self, filepath, memory = False):
        self.path = filepath
        self.file = open(self.path)
        self.frame = 0
        self.n_lines = self.__get_number_of_lines()
        self.current_line = 0
        self.saved_line = None
        self.iteration_started = False  
        self.read_whole_content = False
        self.properties_read = False
        self.memory = memory
        self.atoms_per_frame = list()
        self.timesteps = list()

        if memory:
            self.__read_file_content()
            self.timesteps, self.atoms_per_frame = self.__get_traj_properties()
        self.call_frame(self.frame)
        self.__print()
    
    def read_traj(self):
        self.timesteps, self.atoms_per_frame = self.__get_traj_properties()
        return self

    def data(self):
        return numpy.array([line.split() for line in self.current_frame_data[ldump.lines_header_total:]]).astype(float)        

    def cell(self):
        return numpy.array([i.split() for i in self.current_frame_data[ldump.lines_cell[0]:ldump.lines_cell[-1]+1]]).astype(float).tolist()

    def columns(self):     
        return self.current_frame_data[ldump.line_column_names].split()[2:]
    
    def df_frame(self):
        return pandas.DataFrame(data=self.data(), columns=self.columns())

    def __read_file_content(self):
        self.file_content = self.file.readlines()
        self.file.close()
        self.read_whole_content = True
        return self

    def __get_number_of_lines(self):
        with open(self.path, "r",encoding="utf-8",errors='ignore') as f:
            return (sum(bl.count("\n") for bl in helper_functions.blocks(f)))
    
    def read_lines(self, lines_of_interest):
        lines_to_return = list()
        self.init_line = self.current_line
        lines_of_interest = helper_functions.to_array(lines_of_interest)
        if numpy.max(lines_of_interest)>self.n_lines:
            print('Requested number of line is larger then total lines in trajectory!')

        else:      
            if ((self.saved_line!= type(None)) and len(lines_of_interest)==1 and any(lines_of_interest==self.init_line-1)):
                lines_to_return.append(self.saved_line)
                return lines_to_return
            else:
                if not helper_functions.check_greater(lines_of_interest, self.init_line):
                    self.file.seek(0)
                    self.current_line = 0
                    self.init_line = 0
                for pos, l_num in enumerate(self.file):
                    if pos+self.init_line in lines_of_interest:
                        lines_to_return.append(l_num.replace("\n", ""))
                    if pos+self.init_line >= numpy.max(lines_of_interest):
                        break
                self.current_line = pos+self.init_line+1
                self.saved_line = l_num.replace("\n", "")
                return lines_to_return

    def call_frame(self, frame_number):
        if frame_number == self.frame and frame_number !=0:
            return self
        else:
            self.frame = frame_number
            if self.read_whole_content == True:
                self.current_frame_data = self.file_content[self.start_line_per_frame[self.frame]:self.start_line_per_frame[self.frame]+self.atoms_per_frame[self.frame]+ldump.lines_header_total]
                return self
            if self.read_whole_content == False:
                if self.properties_read == True:
                    lines = numpy.arange(self.start_line_per_frame[self.frame],self.start_line_per_frame[self.frame]+self.atoms_per_frame[self.frame]+ldump.lines_header_total+1,1)
                    frame = self.read_lines(lines)
                    self.current_frame_data = frame
                    return self
                if self.properties_read == False:
                    if frame_number >= len(self.timesteps):
                        if len(self.atoms_per_frame)!=0:
                            line = numpy.cumsum(numpy.array(self.atoms_per_frame)+ldump.lines_header_total)[-1]
                        else:
                            line = 0
                        while frame_number >= len(self.timesteps):
                            if line>0 and line > self.n_lines-(self.atoms_per_frame[-1]+ldump.lines_header_total):
                                raise ValueError('Timestep {} can not be found in the Trajectory'.format(frame_number))

                            self.timesteps.append(int(self.read_lines(int(line+ldump.line_timestep))[0]))
                            self.atoms_per_frame.append(int(self.read_lines(int(line+ldump.line_atom_count))[0]))
                            line += self.atoms_per_frame[-1]+ldump.lines_header_total                   
                        if line > self.n_lines:
                            raise ValueError('Timestep {} can not be found in the Trajectory: {}'.format(frame_number))
                        self.start_line_per_frame = numpy.hstack(([0], numpy.cumsum(numpy.array(self.atoms_per_frame) + ldump.lines_header_total)[:-1]))
                        lines = numpy.arange(self.start_line_per_frame[self.frame],self.start_line_per_frame[self.frame]+self.atoms_per_frame[self.frame]+ldump.lines_header_total,1)
                        frame = self.read_lines(lines)
                        self.current_frame_data = frame
                        return self
                    else:
                        lines = numpy.arange(self.start_line_per_frame[self.frame],self.start_line_per_frame[self.frame]+self.atoms_per_frame[self.frame]+ldump.lines_header_total,1)
                        frame = self.read_lines(lines)
                        self.current_frame_data = frame
                        return self

    def __get_traj_properties(self):
        if self.memory == True:
            timesteps = list()
            atoms_per_frame = list()
            line = 0
            while line < self.n_lines:
                timesteps.append(int(self.file_content[line+ldump.line_timestep]))
                atoms_per_frame.append(int(self.file_content[line+ldump.line_atom_count]))
                line = numpy.cumsum(numpy.array(atoms_per_frame)+ldump.lines_header_total)[-1]
            self.start_line_per_frame = numpy.hstack(([0], numpy.cumsum(numpy.array(atoms_per_frame) + ldump.lines_header_total)[:-1]))
            self.properties_read = True
            return timesteps, atoms_per_frame 

        if self.memory == False:
            timesteps = list()
            atoms_per_frame = list()
            line = 0
            timesteps.append(int(self.read_lines(line+ldump.line_timestep)[0]))
            atoms_per_frame.append(int(self.read_lines(line+ldump.line_atom_count)[0]))
            while line+atoms_per_frame[-1]+ldump.lines_header_total < self.n_lines:
                line += atoms_per_frame[-1]+ldump.lines_header_total
                timesteps.append(int(self.read_lines(line+ldump.line_timestep)[0]))
                atoms_per_frame.append(int(self.read_lines(line+ldump.line_atom_count)[0]))
            self.start_line_per_frame = numpy.hstack(([0], numpy.cumsum(numpy.array(atoms_per_frame) + ldump.lines_header_total)[:-1]))
            self.properties_read = True
            return timesteps, atoms_per_frame 

    def __print(self):
        if self.read_whole_content == True:
            print('Loaded LAMMPS trajectory file "{file}" containing {frames} frames in memory.'.format(file=self.path, frames=self.n_frames))
        if self.read_whole_content == False:
            print('Loaded LAMMPS trajectory file "{file}" with {lines} total lines.'.format(file=self.path, lines=self.n_lines))

    def __iter__(self):
        print('test')
        self.call_frame(0)
        self.frame = 0

        # self.current_frame_data = self.call_frame(self.frame)
        return self

    def __next__(self):
        if self.frame < len(self.timesteps):
            if self.iteration_started:
                self.frame += 1
            self.iteration_started = True 
            self.call_frame(self.frame)
            return self
        else:
            raise StopIteration

    def __getitem__(self, x):
        self.call_frame(x)
        self.frame = x
        return self

    def __exit__(self):
        self.file.close()