#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 11:25:32 2023

@author: saumya
"""

import control
import slycot
import state_space as ss
import getturb as ti

# import state space of the system
# get input and plot the time response

def getss(dx):
    A1 = ss.longitudinalss(dx)
    A2 = ss.lateralss(dx)
    