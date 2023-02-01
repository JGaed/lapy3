#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:46:57 2020
@author: Johannes Gäding
"""

import numpy
import pandas

class system:
    def __init__(self, positions, box, pbc = [1,1,1]):
        self.positions = positions.astype(float)
        self.pbc = pbc      
        self.box = box
        
        self.__set_up_box()
        self.box_length = [self.lx, self.ly, self.lz]
        self.box_limits = [[self.xlo, self.xhi], [self.ylo, self.yhi], [self.zlo, self.zhi]]

    def __set_up_box(self):
        if numpy.shape(self.box)==(3,):
            self.xlo, self.xhi = 0, self.box[0]
            self.ylo, self.yhi = 0, self.box[1]
            self.zlo, self.zhi = 0, self.box[2]
        elif numpy.shape(self.box)==(3,2):
            self.xlo, self.xhi = self.box[0][0], self.box[0][1]
            self.ylo, self.yhi = self.box[1][0], self.box[1][1]
            self.zlo, self.zhi = self.box[2][0], self.box[2][1]
        else:
            raise Exception('Provided box is not in the corract shape. Please provide the boxsize either as (3,) or (3,2) array. [lx, ly, lz] or [[xlo, xhi], [ylo, yhi], [zlo, zhi]]')
        self.lx, self.ly, self.lz = self.xhi - self.xlo, self.yhi - self.ylo, self.zhi - self.zlo

    def self_distances(self):
        self.x_dist = numpy.transpose(self.positions[:,0][numpy.newaxis])-self.positions[:,0]
        self.y_dist = numpy.transpose(self.positions[:,1][numpy.newaxis])-self.positions[:,1]
        self.z_dist = numpy.transpose(self.positions[:,2][numpy.newaxis])-self.positions[:,2]
        if self.pbc[0] == 1:
            self.x_dist[numpy.abs(self.x_dist)>=self.lx] = self.x_dist[numpy.abs(self.x_dist)>=self.lx]-(numpy.fix(self.x_dist[numpy.abs(self.x_dist)>=self.lx]/self.lx)*self.lx)
        if self.pbc[1] == 1:
            self.y_dist[numpy.abs(self.y_dist)>=self.ly] = self.y_dist[numpy.abs(self.y_dist)>=self.ly]-(numpy.fix(self.y_dist[numpy.abs(self.y_dist)>=self.ly]/self.ly)*self.ly)
        if self.pbc[2] == 1:
            self.z_dist[numpy.abs(self.z_dist)>=self.lz] = self.z_dist[numpy.abs(self.z_dist)>=self.lz]-(numpy.fix(self.z_dist[numpy.abs(self.z_dist)>=self.lz]/self.lz)*self.lz)

        self.r_dist = numpy.sqrt(self.x_dist**2+self.y_dist**2+self.z_dist**2)

        return self.r_dist

    def distances(self, second_positions):
        self.x_dist = numpy.transpose(self.positions[:,0][numpy.newaxis])-second_positions[:,0]
        self.y_dist = numpy.transpose(self.positions[:,1][numpy.newaxis])-second_positions[:,1]
        self.z_dist = numpy.transpose(self.positions[:,2][numpy.newaxis])-second_positions[:,2]
        if self.pbc[0] == 1:
            self.x_dist[numpy.abs(self.x_dist)>=self.lx] = self.x_dist[numpy.abs(self.x_dist)>=self.lx]-(numpy.fix(self.x_dist[numpy.abs(self.x_dist)>=self.lx]/self.lx)*self.lx)
        if self.pbc[1] == 1:
            self.y_dist[numpy.abs(self.y_dist)>=self.ly] = self.y_dist[numpy.abs(self.y_dist)>=self.ly]-(numpy.fix(self.y_dist[numpy.abs(self.y_dist)>=self.ly]/self.ly)*self.ly)
        if self.pbc[2] == 1:
            self.z_dist[numpy.abs(self.z_dist)>=self.lz] = self.z_dist[numpy.abs(self.z_dist)>=self.lz]-(numpy.fix(self.z_dist[numpy.abs(self.z_dist)>=self.lz]/self.lz)*self.lz)

        distances = numpy.sqrt(self.x_dist**2+self.y_dist**2+self.z_dist**2)

        return distances

    def density_profile(self, axis, bin_width=0.5, min_coord = None, max_coord = None):
        if min_coord==None:
            min_coord = self.box_limits[axis][0]
        if max_coord==None:
            max_coord = self.box_limits[axis][1]
        bins = numpy.arange(min_coord, max_coord, bin_width)
        hist_data = numpy.histogram(numpy.digitize(self.positions[:,axis], bins), bins=bins)
        plot_bins = (bins+bin_width/2)[:-1]

        return hist_data[0], plot_bins

# import numpy as np
# import freud as fd

# box1 = fd.box.Box.cube(L=5)
# freund_dis = box1.compute_all_distances(coords,coords) 

# traj1 = xyz_trajectory('au100-8x8-pos-1.xyz')
# coords = traj1.positions()
# lx =5
# ly =5
# lz =5

# rmax = np.sqrt(lx**2+ly**2+lz**2)


# pbc1 = [lx, ly, lz]

# sys1 = system(coords, pbc1)
# own_dis = sys1.distances

# x_dist = coords[:,0][np.newaxis].T-coords[:,0]
# y_dist = coords[:,1][np.newaxis].T-coords[:,1]
# z_dist = coords[:,2][np.newaxis].T-coords[:,2]

# x_dist[x_dist>lx] = x_dist[x_dist>lx]-np.fix(x_dist[x_dist>lx]/lx)*lx

# y_dist[y_dist>ly] = y_dist[y_dist>ly]-np.fix(y_dist[y_dist>ly]/ly)*ly
# z_dist[z_dist>lz] = z_dist[z_dist>lz]-np.fix(z_dist[z_dist>lz]/lz)*lz

# r = np.sqrt(x_dist**2+y_dist**2+z_dist**2)


# box1 = fd.box.Box.cube(L=5)
# freund_dis = box1.compute_all_distances(coords,coords) 

# pbc1 = [23.447,23.447, 50]
# coords = traj1.positions()
# sys1 = system(coords, pbc1)

# sum_dens = np.zeros(np.size(sys1.density_profile(2)[0]))
# bins = sys1.density_profile(2)[1]

# for i in traj1:
#     coords = i.positions()
#     print(coords)
#     print(i.frame)
#     sum_dens = sum_dens + system(coords, pbc1).density_profile(2)[0]

# dens = sum_dens/traj1.n_frames
