#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 11 16:49:00 2022
Constraints for implementing Particle Swarm Optimization Algorith
(1) In longitudinal flight only assuming that in longitudinal flight, at equiibrium q = 0 from the equation alphadot = q - gammadot
@author: saumya
"""

import numpy as np
import math
from numpy.linalg import inv
import AeroForcesDECOL as AeroForces

def Constraints_DEP(x, fix, CoefMatrix, atmo, g, PropWing):
    """function defining constraints for power minimization
    inputs:
        -x =[alpha, theta, delta_a, delta_e, delta_r, delta_i]
        x is the state to determine
        length of x except the propulsion levels is 5
        -fix = [V, gamma]
        fix is the vector of parameters whom are fixed by the user
        
        Assuming flight in only longitudinal direction
    """

    rho = atmo[1]

    # --- Now prepare variables for equations ---
    V=fix[0]
    alpha=x[0]
    beta=0
    gamma=fix[2]
    omega=0
    p=0
    q=0
    r=0
    phi=0
    theta=x[1]
    I=np.array([ [g.Ix, 0, -g.Ixz], [0, g.Iy, 0], [-g.Ixz, 0, g.Iz] ])
    
    # --- Compute aerodynamic forces ---
    # Here subvector  must be : (alpha, beta, p, q, r, da, de,dr)
    sub_vect=np.array([alpha,beta,p,q,r])
    sub_vect=np.append(sub_vect,[x[2],x[3],x[4]]) # Rudder is allowed
    # The velocity seen by all engines is not same due to sweep and roll, as a result, the velocity vector acting on these are different
    V_vect = np.ones(g.N_eng) * V * np.cos(g.wingsweep)

    Fx_body=g.Thrust(x[-g.N_eng:],V_vect)
    Mx = g.Torque(x[-g.N_eng:],V_vect)
    # Convert Thrust in body frame to thrust in aerodynamic frame :  TRUE only for longitudinal flight
    Tab = [[np.cos(alpha), 0, np.sin(alpha)],
           [0, 1, 0],
           [-np.sin(alpha), 0, np.cos(alpha)]]
    Fx_aero = np.matmul(Tab,Fx_body)
    Mx_aero = Tab @ Mx
    
    # Convert thrust in Tc for patterson
    Tc = g.DefaultProp(x[-g.N_eng:],V_vect)/(2*rho*g.Sp*V**2)   
    F=AeroForces.CalcForce_aeroframe_DEP(V, np.copy(CoefMatrix), np.copy(sub_vect), Tc, atmo, g, PropWing)
    
    # Now sum up the constraints:
    A=np.zeros(6+g.inop)
    """
    A0 = x
    A1 = y
    A2 = z
    A3 = l
    A4 = m
    A5 = n
    A6 = phi
    A7 = theta
    A8 = gamma
    A9 = Omega
    """
    A[0] = -9.81*np.sin(gamma)+F[0]/g.m+Fx_aero[0]/g.m
    A[1] = F[1] # There should be no force along y axis in longitudinal flight
    A[2] = g.m*9.81*np.cos(gamma)/(g.m*V) + F[2]/(g.m*V) + Fx_aero[2]/(g.m*V) 
    A[3:6] = np.array([Mx_aero[0], Mx_aero[1], Mx_aero[2]])+F[3:6]

    """To ensure that the constraints are well satisfied, the constraints are modelled as inequality constraints with a tolerance for constraints as 10^-5"""
    return (np.ones(6)*2.5e-9 - np.dot(A,A))  

def fobjectivePower(x, fix, rho, g):
    
    # Objective Function for Power Minimization
    #Power=np.sum(x[-g.N_eng:])*2*g.P_var/float(g.N_eng)*rho/1.225/1000000
    Power = np.sum(x[-g.N_eng:])*2*g.P_var/float(g.N_eng)/1000000
    return Power

def fobjectivedx(x, fix, Coef, atmo, g, PW):
    J = np.sum(x[-g.N_eng:]**2)/8;
    return J

def fobjectivePropWingInterac(x, fix, rho, g):

    Dx = x[-g.N_eng:]
    MeanDx = np.mean(Dx)
    stdDx = np.std(Dx)
    return MeanDx*0.5+stdDx*0.5

def fobjectiveDrag(x, fix, CoefMatrix , atmo, g, PropWing):
     rho = atmo[1]
     V=fix[0]
     alpha=x[0]
     beta=fix[1]
     p=x[1]
     q=x[2]
     r=x[3]
     sub_vect=np.array([alpha,beta,p,q,r])
     sub_vect=np.append(sub_vect,[x[6],x[7],x[8]])
     V_vect = np.ones(g.N_eng) * V * np.cos((-np.sign(g.PosiEng)) * beta + g.wingsweep) - r * g.PosiEng
     Tc = g.DefaultProp(x[-g.N_eng:],V_vect)/(2*rho*g.Sp*V**2) 
     F=AeroForces.CalcForce_aeroframe_DEP(V, np.copy(CoefMatrix), np.copy(sub_vect), Tc, atmo, g, PropWing)
     
     # We send the negative of this value 
     return -F[0]


def Jac_DEP(x, fix, CoefMatrix, atmo, g, PropWing, h):
    # function to compute the jacobian at a steady state
    # the function is hard coded inside
    # inputs :
    #       -x : steady state vector
    #       -fixtuple : tuple of (fixed param, function param)
    #       -h : step to compute derivative
    
    nfx=9 # number of equations for flight analysis (V, beta, alpha, p, q, r, phi, theta, gamma)
    # As gamma is a parameter in the flight equation (gamma_dot not computed),
    # The vector of accelerations is : [V,beta,alpha,p,q,r,phi,theta] = nfx-1
    
    step_vec=x*h
    
    for i in range(len(step_vec)):
        # check for zeros
        if step_vec[i]<1e-4:
            step_vec[i]=0.001
     
#    fx=Constraints_DEP(x, *fixtuple)
    
    dx=np.zeros((nfx-1,len(x)+3))
    fixtuple=(fix, CoefMatrix, atmo, g, PropWing)
    
    # Compute derivative using centered difference
    # Accelerations due to a small change in velocity
    fix_plus=fix+np.append([fix[0]*h/2.0],np.zeros((len(fix)-1)))
    fix_minus=fix-np.append([fix[0]*h/2.0],np.zeros((len(fix)-1)))
    
    tuple_plus=(fix_plus, CoefMatrix, atmo, g, PropWing)
    tuple_minus=(fix_minus, CoefMatrix, atmo, g, PropWing)
    
    diff=(Constraints_DEP(x,*tuple_plus)-Constraints_DEP(x,*tuple_minus))/(fix[0]*h)
    dx[:,0]=diff[0:nfx-1]
    
    # Accelerations due to a small change in side-slip
    beta_step=np.zeros((len(fix)))
    beta_step[1]=h/2
    fix_plus=fix+beta_step
    fix_minus=fix-beta_step
    
    tuple_plus=(fix_plus, CoefMatrix, atmo, g, PropWing)
    tuple_minus=(fix_minus, CoefMatrix, atmo, g, PropWing)
    
    diff=(Constraints_DEP(x,*tuple_plus)-Constraints_DEP(x,*tuple_minus))/(beta_step[1]*2)
    dx[:,1]=diff[0:nfx-1]
    
    # Accelerations due to a small change in gamma
    gamma_step=np.zeros((len(fix)))
    gamma_step[2]=h/2
    fix_plus=fix+gamma_step
    fix_minus=fix-gamma_step
    
    tuple_plus=(fix_plus, CoefMatrix, atmo, g, PropWing)
    tuple_minus=(fix_minus, CoefMatrix, atmo, g, PropWing)
    
    diff=(Constraints_DEP(x,*tuple_plus)-Constraints_DEP(x,*tuple_minus))/(gamma_step[2]*2)
    dx[:,2]=diff[0:nfx-1]
    
    # Now all acceleration due to a small of each variables in x
    for j in range(len(x)):
        activex=np.zeros((len(x)))
        activex[j]=1
        dfx=(Constraints_DEP(x+activex*step_vec/2,*fixtuple)-Constraints_DEP(x-activex*step_vec/2,*fixtuple))/np.dot(activex,step_vec)
        dx[:,j+3]=dfx[0:nfx-1]

    # Optionally decouple matrix
    return dx
