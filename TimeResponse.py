#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 11:25:32 2023

@author: saumya
"""
import numpy as np
import control
import slycot
import state_space as ss
import getturb as ti
import matplotlib.pyplot as plt
import matplotlib.colors as colors

# import state space of the system
# get input and plot the time response

def getss(dx, dxt):
    A = ss.completess(dx)
    #A = np.vstack([A1, A2])
    #print(np.size(A))
    B = dxt
    #print(np.size(B))
    # Assuming all the state values are available
    C = np.identity(8)
    D = np.zeros((8,6))
    sys = control.ss(A, B, C, D)
    # Here, the turbulence is treated as the input
    return sys

def plotresponse(x0, sys):
    U,t = ti.sendturb()
    t = np.arange(0, 20, 0.2)
    R = control.forced_response(sys, t, U, x0)
    
    # plot the response
    plt.grid()
    plt.plot(R.t,R.y[0])
    plt.plot(R.t,R.y[1])
    plt.plot(R.t,R.y[2])
    plt.plot(R.t,R.y[3])
    plt.plot(R.t,R.y[4])
    plt.plot(R.t,R.y[5])
    plt.plot(R.t,R.y[6])
    plt.plot(R.t,R.y[7])
    plt.show()
    # Add legends to all the curves and see time response when the gust stops
    
    return R