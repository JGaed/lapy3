#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 01.02.2023
@author: Johannes Gäding
"""

from distutils.core import setup

setup(name='lapy3',
      version='1.0',
      description='Utility package to read LAMMPS and related Molecular dynamics files',
      author='Johannes Gaeding',
      author_email='johannes.gaeding@tuhh.de',
      url='https://github.com/JGaed/lapy3',
      setup_requires=["numpy", "pandas"],
      install_requires=["numpy", "pandas"], 
      packages=['pickle_functions', 'lammps_py3', 'lammps', 'trajectory', 'functions', 'system']
     )
