
""" The main_DEP.py calls the necessary functions from other packages and executes the following functions:
    1) Get all the aerodynamic coefficients for the aircraft at the required velocity and flight parameters
    2) Include aero-propulsive interactions
    3) Calculate the thrust and moment needed from the flight equations
    4) Optimally distribute thrust among the engines and control surfaces """
""" - Modified Eric Nguyen Van and David Planas Andres 's work"""
""" For the pupose of Optimal Thrust Allocation """
""" - Modified by Saumya Sarawagi"""

# Import required inbuilt packages
import numpy as np
import math
import scipy.linalg
import scipy.io #input/output with matlab
from scipy.optimize import  minimize
from datetime import datetime
from pyswarm import pso

# Import DECOL packages
import AeroForcesDECOL
import DECOLgeometry
import ReadFileUtils
import constraints_PSO as e
import PattersonAugmented as PA

# Atmospheric conditions for H = 0m
H = 0 # Altitude(m)
a = 340.3 # Velocity of Sound at 0m
rho = 1.225 # Density of air at sea level as obtained from si2py.txt -> Eric Nguyen Van
atmo = [a, rho]

# Used to obtain Aerodynamic Coefficients at different velocities 
Velocities=(10,15,20,25,30,35)
rho_vec=(1.225,1.225,1.225,1.225,1.225,1.225)
# Mach = [v/a for v in list(Velocities)]
Mach=np.ones((len(Velocities),1))*0.0001 # To have incompressible flow as the speds are considered very low

# Define DECOL Parameters
inop_eng = 0 # Number of engines that are inoperative
g = DECOLgeometry.data(inop_eng, r=0.113 / 2, rf=0.1865 / 2, zw=0.045)

# Constant Flight Parameters
V = 23.5   # Velocity (m/s)
M = V/a
beta = 0 / 180 * math.pi
gamma = 3 / 180 * np.pi  # math.atan(0/87.4)#/180*math.pi # 3% slope gradient # 6.88m/s vertical
R = 0  # in meters the turn radius
g.P_var = 8 * 14.4 * 4  # I*V*N_eng/2    

# Constraints 
ThrottleMax = 1  
ThrottleMin = 0.0001  
    # Control Surface Constraints 
deltaAMin = -20*math.pi/180 # Ailerons
deltaAMax = 20*math.pi/180
deltaEMin = -20*math.pi/180 # Elevators
deltaEMax = 20*math.pi/180
deltaRMin = -25*math.pi/180 # Rudder
deltaRMax = 25*math.pi/180
    # Angle Constraints
alphaMin = -2*math.pi/180
alphaMax = 8*math.pi/180
phiMin = -30*math.pi/180
phiMax = 30*math.pi/180
thetaMin = -30*math.pi/180
thetaMax = 30*math.pi/180
                                                                          
g.FlapDefl = 0  # Standard flap deflection (degrees) is 14 but for our purpose we consider 0 flap deflection
g.VelFlap = 12.5  # Maximum velocity at which flap are deployed (m/s)                                                      

# Used in the Patterson modulus for modelling stall in accordance with Antony Jameson's proposal
g.alpha_max = 10 / 180 * np.pi
g.alpha_max_fl = 10 / 180 * np.pi

# FLight measured Cd0:
g.CD0T = 0.0636         # Global one  extracted from flight not stab the file
                                                            
# Extracting the aerodynamic coefficients
path = 'DECOL_STAB/'  
filenameNoFin = [path + '_FinLess_Vinf10000.stab',
                 path + '_FinLess_Vinf15000.stab',
                 path + '_FinLess_Vinf20000.stab',
                 path + '_FinLess_Vinf25000.stab',
                 path + '_FinLess_Vinf30000.stab',
                 path + '_FinLess_Vinf35000.stab']
MatrixNoFin = ReadFileUtils.ReadStabCoef(filenameNoFin)
CoefMatrix=g.NicolosiCoef(MatrixNoFin[:,1:], Mach)
Coef=AeroForcesDECOL.CoefInterpol(V, CoefMatrix, Velocities)

# Defining the Propulsion & Wing Interaction
g.PolarFlDeflDeg = 5
g.PolarAilDeflDeg = 5
PropPath = "DECOL_FEM/"
PropFilenames = {'fem':[PropPath+"_FinLess_Vinf10000.0"],
                 'AirfoilPolar':PropPath+"S3010_XTr10_Re350.txt",
                 'FlapPolar':PropPath+"S3010_XTr10_Re350_fl5.txt",
                 'AileronPolar':PropPath+"S3010_XTr10_Re350_fl5.txt"} # format for prop file : [[Cldist=f(M)],polar clean airfoil, polar flap, polar aile]
PW = PA.PropWing(g,PropFilenames)
#PW.AoAZero[:,-1] = PW.AoAZero[:,-1] + 3.2/180*np.pi # Correction for angle of incidence of wing
PW.AoAZero[:,0] = PW.AoAZero[:,0]*10**(-3)
PW.CLslope[:,0] = PW.CLslope[:,0]*10**(-3)
PW.AoAZero[:,1] = PW.AoAZero[:,1]*10**(-6)
PW.CLslope[:,1] = PW.CLslope[:,1]*10**(-6)         # In order to express in S.I. units as DECOL.vsp3 yields in mm
PW.AoAZero[:,2] = PW.AoAZero[:,2]*10**(-3)
PW.CLslope[:,2] = PW.CLslope[:,2]*10**(-3)
PW.DeltaCL_a_0 = 1 #CL_alpha correction factor

g.nofin = False
g.DisplayPatterInfo = False

# For PSO algorithm applied only in longitudinal flight
# x =[alpha, theta, delta_a, delta_e, delta_r, delta_i] where delta i has 8 elelments

x0=np.array([5*math.pi/180, 0.0, 0.0, 0.0, 0.0]) # Assuming initial alpha to be 5degrees
low_bnds = [alphaMin, thetaMin, deltaAMin, deltaEMin, deltaRMin, ThrottleMin, ThrottleMin, ThrottleMin, ThrottleMin, ThrottleMin, ThrottleMin, ThrottleMin, ThrottleMin]
up_bnds = [alphaMax, thetaMax, deltaAMax, deltaEMax, deltaRMax, ThrottleMax, ThrottleMax, ThrottleMax, ThrottleMax, ThrottleMax, ThrottleMax, ThrottleMax, ThrottleMax]

# Complete the vectors with engines:
eng_vec = np.array([0.4] * g.N_eng)
x0 = np.append(x0, eng_vec)
    
# --- imposed conditions ---
# fix = [V, beta, gamma, omega, H]
if R == 0:
    omega = 0
else:
    omega = V * math.cos(gamma) / R

fixtest = np.array([V, beta, gamma, omega])
# put everything in tuples for passing to functions
argscons = (np.copy(fixtest), np.copy(Coef), atmo, g, PW)  # fix, CoefMatrix,Velocities, rho, g

# PSO
t0 = datetime.now()
xopt, fopt = pso(e.fobjectivedx, low_bnds, up_bnds, ieqcons=[], f_ieqcons= e.Constraints_DEP, args= argscons, kwargs={},
    swarmsize=10, omega=0.84, phip=0.95, phig=1.6, maxiter=100, minstep=1e-8,
    minfunc=1e-8, debug=False) # Make constraints a part of the objective function - 
                 
                 
                 
t1 = datetime.now()
print("Evaluation_time :" , t1-t0)
print(xopt)
print(fopt)

# check if constraints are validated
constraints_calc=e.Constraints_DEP(xopt,*argscons)
print("\nConstraints")
print(constraints_calc)















