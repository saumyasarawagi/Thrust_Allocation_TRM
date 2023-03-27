# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 22:22:50 2023

@author: tusha
"""

# Import the classes
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from dryden import DrydenGustModel, Filter


def sendturb():
    # Define the sample time and simulation time
    # Assuming different time scales for the time being
    dt = 0.1
    simulation_time = 5
    t = np.arange(0, simulation_time, dt)

    # Define the aircraft parameters
    b = 2 # Span of the aicraft?
    h = 100
    V_a = 23.5
    meters2feet = 3.281
    feet2meters = 1 / meters2feet
    # Define the turbulence intensity
    intensity = "light"

    # Create the Dryden gust model object
    dryden_model = DrydenGustModel(dt, b, h, V_a, intensity)

    dryden_model.seed(7)
    dryden_model._generate_noise(10)
    dryden_model.reset(dryden_model.noise)
    dryden_model.simulate(int(simulation_time*dt*100))

    #print(dryden_model.vel_lin)
    #print("----------------------------------------------------")
    #print(dryden_model.vel_ang)

    # # Generate the turbulence signals
    gust_u = dryden_model.vel_lin[0]/feet2meters
    gust_v = dryden_model.vel_lin[1]/feet2meters
    gust_w = dryden_model.vel_lin[2]/feet2meters
    gust_p = dryden_model.vel_ang[0]
    gust_q = dryden_model.vel_ang[1]
    gust_r = dryden_model.vel_ang[2]

    # # Plot the generated turbulence signals

    plt.figure()
    plt.plot(t, gust_u, label="gust u")
    plt.plot(t, gust_v, label="gust v")
    plt.plot(t, gust_w, label="gust w")
    plt.xlabel("Time (s)")
    plt.ylabel("Turbulence velocities")
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(t, gust_p, label="gust p")
    plt.plot(t, gust_q, label="gust q")
    plt.plot(t, gust_r, label="gust r")
    plt.xlabel("Time (s)")
    plt.ylabel("Turbulence angular rates")
    plt.legend()
    plt.show()
    
    U = np.zeros((6,100))
    U[0, 10:60] = gust_u
    U[1, 10:60] = gust_v
    U[2, 10:60] = gust_w
    U[3, 10:60] = gust_p
    U[4, 10:60] = gust_q
    U[5, 10:60] = gust_r
    
    return U,t



