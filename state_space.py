#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 11:41:33 2022

@author: saumya
"""

import numpy as np
import math
from numpy.linalg import inv

# The following function forms the longitudinal state space with the following state vectors
# X = [V, theta, alpha, q]; U = [delta_e delta_i]' -- 9 variable output 
# alpha-q and V-gamma
def longitudinalss(dx):
    # Now to get the A matrix for the system
    # Since for longitudinal flight gamma + alpha = theta  -using theta is enough
    A = np.zeros((4,4))
    A[0,0] = dx[0,0];
    A[0,1] = dx[0,2];
    A[0,2] = dx[0,3];
    A[0,3] = dx[0,5];
    
    A[1,0] = dx[2,0]; #---> theta_derivative instead of gamma_derivative for now
    A[1,1] = dx[2,2];
    A[1,2] = dx[2,3];
    A[1,3] = dx[2,5];
    
    A[2,0] = dx[3,0];
    A[2,1] = dx[3,2];
    A[2,2] = dx[3,3];
    A[2,3] = dx[3,5];
    
    A[3,0] = dx[5,0]; 
    A[3,1] = dx[5,2];
    A[3,2] = dx[5,3];
    A[3,3] = dx[5,5];

# To assess effect of control variables obtain the B matrix but for now A is enough for stability matrix

    return A
# The following function forms the lateral state space with the following state vectors
# X = [beta, r, p, phi]; U = [delta_a, delta_r, delta_i]' -- 9 variable output 
# First mode is the pure roll mode
# Second mode is the side-slip oscillation related to beta and r
# Thirds mode is the spiral mode related to phi
def lateralss(dx):
    
    # Now to get the A matrix for the system
    A = np.zeros((4,4))
    A[0,0] = dx[1,1];
    A[0,1] = dx[1,4];
    A[0,2] = dx[1,6];
    A[0,3] = dx[1,7];
    
    A[1,0] = dx[4,1];
    A[1,1] = dx[4,4];
    A[1,2] = dx[4,6];
    A[1,3] = dx[4,7];
    
    A[2,0] = dx[6,1];
    A[2,1] = dx[6,4];
    A[2,2] = dx[6,6];
    A[2,3] = dx[6,7];

    A[3,0] = dx[7,1];
    A[3,1] = dx[7,4];
    A[3,2] = dx[7,6];
    A[3,3] = dx[7,7];

# To assess effect of control variables obtain the B matrix but for now A is enough for stability matrix

    return A


def completess(dx):
    
    A = np.zeros((8,8))
    A[0,0] = dx[0,0];
    A[0,1] = dx[0,8];
    A[0,2] = dx[0,3];
    A[0,3] = dx[0,5];
    A[0,4] = dx[0,1];
    A[0,5] = dx[0,6];
    A[0,6] = dx[0,4];
    A[0,7] = dx[0,7];
    
    A[1,0] = dx[7,0]; #---> theta_derivative instead of gamma_derivative for now
    A[1,1] = dx[7,8];
    A[1,2] = dx[7,3];
    A[1,3] = dx[7,5];
    A[1,4] = dx[7,1];
    A[1,5] = dx[7,6];
    A[1,6] = dx[7,4];
    A[1,7] = dx[7,7];
    
    A[2,0] = dx[2,0];
    A[2,1] = dx[2,8];
    A[2,2] = dx[2,3];
    A[2,3] = dx[2,5];
    A[2,4] = dx[2,1];
    A[2,5] = dx[2,6];
    A[2,6] = dx[2,4];
    A[2,7] = dx[2,7];
    
    A[3,0] = dx[4,0]; 
    A[3,1] = dx[4,8];
    A[3,2] = dx[4,3];
    A[3,3] = dx[4,5];
    A[3,4] = dx[4,1];
    A[3,5] = dx[4,6];
    A[3,6] = dx[4,4];
    A[3,7] = dx[4,7];
    
    A[4,0] = dx[1,0]; 
    A[4,1] = dx[1,8];
    A[4,2] = dx[1,3];
    A[4,3] = dx[1,5];
    A[4,4] = dx[1,1];
    A[4,5] = dx[1,6];
    A[4,6] = dx[1,4];
    A[4,7] = dx[1,7];
    
    A[5,0] = dx[5,0]; 
    A[5,1] = dx[5,8];
    A[5,2] = dx[5,3];
    A[5,3] = dx[5,5];
    A[5,4] = dx[5,1];
    A[5,5] = dx[5,6];
    A[5,6] = dx[5,4];
    A[5,7] = dx[5,7];
    
    A[6,0] = dx[3,0]; 
    A[6,1] = dx[3,8];
    A[6,2] = dx[3,3];
    A[6,3] = dx[3,5];
    A[6,4] = dx[3,1];
    A[6,5] = dx[3,6];
    A[6,6] = dx[3,4];
    A[6,7] = dx[3,7];
    
    A[7,0] = dx[6,0]; 
    A[7,1] = dx[6,8];
    A[7,2] = dx[6,3];
    A[7,3] = dx[6,5];
    A[7,4] = dx[6,1];
    A[7,5] = dx[6,6];
    A[7,6] = dx[6,4];
    A[7,7] = dx[6,7];
    
    return A

def Bforfixedinput(dx):
    
    # Add gamma here as well
    A = np.zeros((8,12))
    c = 0;
    A[0,c] = dx[0,2];
    A[1,c] = dx[7,2];
    A[2,c] = dx[2,2];
    A[3,c] = dx[4,2];
    A[4,c] = dx[1,2];
    A[5,c] = dx[5,2];
    A[6,c] = dx[3,2];
    A[7,c] = dx[6,2];
   
    for i in range(9,20):
        c = c+1;
        A[0,c] = dx[0,i];
        A[1,c] = dx[7,i];
        A[2,c] = dx[2,i];
        A[3,c] = dx[4,i];
        A[4,c] = dx[1,i];
        A[5,c] = dx[5,i];
        A[6,c] = dx[3,i];
        A[7,c] = dx[6,i];
       
    
    return (A)