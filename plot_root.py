#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 15:28:19 2023

@author: saumya
"""
# Plot the root locus of longitudinal eigen values as V changes

import numpy as np
import matplotlib.pyplot as plt


X = np.load("eiglong1.npy")
x = np.load("eiglong2.npy")
X = np.append(X,x)
x = np.load("eiglong3.npy")
X = np.append(X,x)
x = np.load("eiglong4.npy")
X = np.append(X,x)
x = np.load("eiglong5.npy")
X = np.append(X,x)
x = np.load("eiglong6.npy")
X = np.append(X,x)
x = np.load("eiglong7.npy")
X = np.append(X,x)
x = np.load("eiglong8.npy")
X = np.append(X,x)
x = np.load("eiglong9.npy")
X = np.append(X,x)
x = np.load("eiglong10.npy")
X = np.append(X,x)
"""x = np.load("eiglong11.npy")
X = np.append(X,x)"""

con1 = np.zeros(10,dtype=np.complex_)
con2 = np.zeros(10,dtype=np.complex_)
con3 = np.zeros(10,dtype=np.complex_)
con4 = np.zeros(10,dtype=np.complex_)
count = 0;

for i in range(10):
    con1[i] = X[count]
    count = count+1
    con2[i] = X[count]
    count = count+1
    con3[i] = X[count]
    count = count+1
    con4[i] = X[count]
    count = count+1

X1  = con1.real
Y1 =con1.imag
plt.grid()
plt.plot(X1,Y1)
X2  = con2.real
Y2 =con2.imag
plt.plot(X2,Y2)
X3  = con3.real
Y3 =con3.imag
plt.plot(X3,Y3)
X4  = con4.real
# X4 values ae very small and hence the root locus cannot be visualized.
Y4 =con4.imag
plt.plot(X4,Y4)
plt.show()

# It is observed that with velocity the eigen values become more negative i.e the magnitude of both real
# and imaginary part increases. One of the eigen values observes positive value for very low velocities
# Fast poles are observed as the velocity increases

