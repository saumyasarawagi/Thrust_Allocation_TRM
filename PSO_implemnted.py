# -*- coding: utf-8 -*-
"""
Created on Sun May 22 10:57:05 2022

@author: saumya
"""

# Import required libraries 
import numpy as np
import math
from numpy.linalg import inv
import random as rnd
from random import uniform
# For solving the equations
import sympy as sym
from scipy.optimize import fsolve

import AeroForcesDECOL

num_particles = 7 # Number of swarm particles
num_dimensions = 7 # Parameters owned by each dimension 

"""
Use inbuilt pyhton solvers to solve the flight dynamic equations of the DEP aircraft when alpha, p, q, r, and da, de, dr are generated by the swarms
Solving those equations give the value for phi, theta and dx.  
"""
def function(initial, x, fix, CoefMatrix, atmo, g, PropWing):
    """ This function is used to obtain the other parameters such that the constraints are satisfied. 
        x = alpha, p, q, r, da, de, dr - these are the values generated by the swarm
        fix = V, beta, gamma, omega"""
        
        # Since the control parameters are da, de, dr and dx, they will be generated by the swarm instead of alpha, p, q, r, da, de, dr 
        
    """This function is used to obtain the control parameters such that the flight properties satusfy the constraints
        x = dx - these are the values generated by the swarm but because we have 10 equations to satisfy. hence we need 10 variables to satisfy the equations. i.e. only the first 7 are generated by the swarm
        fix = V, beta, gamma, omega"""
    rho = atmo[1]
    V = fix[0]
    beta = fix[1]
    gamma = fix[2]
    omega = fix[-1]
    dx = np.zeros(8)
    for i in range(7):
        dx[i] = x[i]
    # Allocating the initial estimate for the equations' solution
    dx[7] = initial[9]
    alpha = initial[0]
    p = initial[1]
    q = initial[2]
    r = initial[3]
    phi = initial[4]
    theta = initial[5]
    da = initial[6]
    de = initial[7]
    dr = initial[8]
    
    I = np.array([[g.Ix, 0, -g.Ixz], [0, g.Iy, 0], [-g.Ixz, 0, g.Iz]])
    # --- Compute aerodynamic forces ---
    #here subvector  must be : (alpha, beta, p, q, r, da, de,dr)
    # Dimension mismatch as a result make da, de and dr also a part of equation solver and remove one equation. Compare with constant thrust values and maybe add the extra equation as a penalty along with other constraints
    sub_vect = np.array([alpha, beta, p, q, r])
    sub_vect = np.append(sub_vect, [da, de, dr])
    V_vect = np.ones(g.N_eng) * V * np.cos((-np.sign(g.PosiEng)) * beta + g.wingsweep) - r * g.PosiEng
    
    # Solving flight dynamic equations to obtain the remaining flight parameters using fsolve

    Fx_body=g.Thrust(dx,V_vect)
    Mx = g.Torque(dx,V_vect)
    # Convert Thrust in body frame to thrust in aerodynamic frame
    Tab = [[np.cos(alpha)*np.cos(beta), np.sin(beta), np.sin(alpha)*np.cos(beta)],
           [-np.cos(alpha)*np.sin(beta), np.cos(beta), -np.sin(alpha)*np.sin(beta)],
           [-np.sin(alpha), 0, np.cos(alpha)]]
    Fx_aero = np.matmul(Tab,Fx_body)
    Mx_aero = Tab @ Mx
    
    # Convert thrust in Tc for patterson
    Tc = g.DefaultProp(dx,V_vect)/(2*rho*g.Sp*V**2)   
    F=AeroForcesDECOL.CalcForce_aeroframe_DEP(V, np.copy(CoefMatrix), np.copy(sub_vect), Tc, atmo, g, PropWing)
    
    # Now sum up the constraints:
    sinbank=np.sin(theta)*np.cos(alpha)*np.sin(beta) + np.cos(beta)*np.cos(theta)*np.sin(phi)-np.sin(alpha)*np.sin(beta)*np.cos(theta)*np.cos(phi)
    cosbank=np.sin(theta)*np.sin(alpha)+np.cos(beta)*np.cos(theta)*np.cos(phi) 
    A=np.zeros(10+g.inop)
    A[0]=-9.81*np.sin(gamma)+F[0]/g.m+Fx_aero[0]/g.m
    A[1]=(p*np.sin(alpha) - r*np.cos(alpha))+g.m*9.81*sinbank/(g.m*V) + F[1]/(g.m*V) + Fx_aero[1]/(g.m*V)
    A[2]=-(np.sin(beta)*(p*np.cos(alpha)+r*np.sin(alpha))-q*np.cos(beta))/np.cos(beta)+ 9.81*cosbank/(V*np.cos(beta)) + F[2]/(g.m*V*np.cos(beta))+Fx_aero[2]/(g.m*V*np.cos(beta))
    A[3:6] = np.dot(inv(I), np.array([Mx_aero[0], Mx_aero[1], Mx_aero[2]])+F[3:6]-np.cross(np.array([p, q, r]), np.dot(I, np.array([p, q, r]))))
    A[6]=p+q*np.sin(phi)*np.tan(theta)+r*np.cos(phi)*np.tan(theta)
    A[7]=q*math.cos(phi) -r*math.sin(phi)
    A[8]=-np.sin(gamma)+np.cos(alpha)*np.cos(beta)*np.sin(theta)-np.sin(beta)*np.sin(phi)*np.cos(theta)-np.sin(alpha)*np.cos(beta)*np.cos(phi)*np.cos(theta)
    A[9]=-omega + (q*np.sin(phi)+r*np.cos(phi))/np.cos(theta)
    
    
    # Add dx equal constraint in longitudinal flight and add inoperative engine condition
    return A

def solve(initial, x, fix, CoefMatrix, atmo, g, PropWing):
    z = fsolve(function, initial, args = (x, fix, CoefMatrix, atmo, g, PropWing)) 
    return z

def fitness(x, fix, CoefMatrix, atmo, g, PropWing):
    
    fitness = 0
    initial =  [5.0*math.pi/180, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4] 
    z = solve(initial,  x, fix, CoefMatrix, atmo, g, PropWing)
    print(z)
    # Add fitness for the bound values not being satisfied for alpha, p, q, r, phi, theta, da, de, dr and dx[7]
    if z[0]<-2*math.pi/180 or z[0]> 8*math.pi/180:
        fitness += 100
    if z[1]<-0.2 or z[1]> 0.2:
        fitness += 100
    if z[2]<-0.2 or z[2]> 0.2:
        fitness += 100
    if z[3]<-0.2 or z[3]> 0.2:
        fitness += 100
    if z[4]<-30*math.pi/180 or z[4]> 30*math.pi/180:
        fitness += 100
    if z[5]<-30*math.pi/180 or z[5]> 30*math.pi/180:
        fitness += 100
    if z[6]<-20*math.pi/180 or z[6]> 20*math.pi/180:
        fitness += 100
    if z[7]<-20*math.pi/180 or z[7]> 20*math.pi/180:
        fitness += 100
    if z[8]<-25*math.pi/180 or z[8]> 25*math.pi/180:
        fitness += 100
    if z[9]<0.1 or z[9]> 1:
        fitness += 100
    x = np.array(x)
    dx = np.zeros(8)
    dx[0:7] = x
    dx[7] = z[9]
    fitness += np.sum(dx**2)# Square of thrust fraction of each engine
    return fitness


# Initial random values for the parameters generated by the swarm
x = [None]*num_dimensions
for i in range(num_particles):
    dx = np.random.uniform(0.1, 1, 7)
    temp = dx.tolist()
    x[i] = temp
    temp = []

# Particle Swarm Optimization Method
r1 = rnd.random()
r2 = rnd.random()
values = []
radius = []
thangle = []
velr = []
velth = []
mass = []
# p_best = []
# t_best = []
bounds = [[0.1,1], [0.1,1], [0.1,1], [0.1,1], [0.1,1], [0.1,1], [0.1,1]]
class Particle():
    def __init__(self, x):
        self.position_i=[]          # particle position
        self.velocity_i=[]          # particle velocity
        self.pos_best_i=[]          # best position individual
        self.err_best_i=-1          # best error individual
        self.err_i=-1               # error individual
        for i in range(0,num_dimensions):
            self.velocity_i.append(uniform(-1,1))
            self.position_i.append(x[i])
   
    # Evaluate current fitness
    def evaluate(self,fitness, fix, CoefMatrix, atmo, g, PropWing):
        self.err_i=fitness(self.position_i, fix, CoefMatrix, atmo, g, PropWing)

        # check to see if the current position is an individual best
        if self.err_i<self.err_best_i or self.err_best_i==-1:
            self.pos_best_i=self.position_i.copy()
            self.err_best_i=self.err_i
            
    def update_velocity(self,pos_best_g):
        """Tune these values to improve model performance"""
        w=0.50       # constant inertia weight (how much to weigh the previous velocity)
        c1=1     # cognitive constant
        c2=2     # social constant
        
        for i in range(0,num_dimensions):
            r1=rnd.random()
            r2=rnd.random()
            vel_cognitive=c1*r1*(self.pos_best_i[i]-self.position_i[i])
            vel_social=c2*r2*(pos_best_g[i]-self.position_i[i])
            self.velocity_i[i]=w*self.velocity_i[i]+vel_cognitive+vel_social       
    
    def update_position(self,bounds):
        for i in range(0,num_dimensions):
            self.position_i[i]=self.position_i[i]+self.velocity_i[i]
            
            # adjust maximum position if necessary
            if self.position_i[i]>bounds[i][1]:
                self.position_i[i]=bounds[i][1]

            # adjust minimum position if neseccary
            if self.position_i[i]<bounds[i][0]:
                self.position_i[i]=bounds[i][0]

#def pso(fix, CoefMatrix, atmo, g, PropWing):
def minimize( fix, CoefMatrix, atmo, g, PropWing, fitness = fitness, inds = x, bounds = bounds, num_particles = num_particles, maxiter = 100, verbose=False):
    global num_dimensions

    num_dimensions=len(x[0])
    err_best_g=-1                   # best error for group
    pos_best_g=[]                   # best position for group

    # establish the swarm
    swarm=[]
    for i in range(0,num_particles):
        swarm.append(Particle(x[i]))

    # begin optimization loop
    i=0
    while i<maxiter:
        if i%50 == 0 & i!=0:
            print(f"{i} epochs done.")       
            
        # cycle through particles in swarm and evaluate fitness
        for j in range(0,num_particles):
            swarm[j].evaluate(fitness,fix, CoefMatrix, atmo, g, PropWing)

            # determine if current particle is the best (globally)
            # While adding an ending criteria, compare it with the case when DEP is not used
            if swarm[j].err_best_i<err_best_g or err_best_g==-1:
                pos_best_g=list(swarm[j].position_i)
                if (err_best_g - swarm[j].err_best_i) < 1e-3 and err_best_g != -1:
                    i = maxiter
                    
                err_best_g=float(swarm[j].err_best_i)     
                print("check:", err_best_g)
        
        # cycle through swarm and update velocities and position
        for j in range(0,num_particles):
            swarm[j].update_velocity(pos_best_g)
            swarm[j].update_position(bounds)
        i+=1

    # print final resultss
    
    print('\nFINAL SOLUTION:')
    print(f'   > {pos_best_g}')
    print(f'   > {err_best_g}\n')

# f = fitness(inds[0])
#minimize()