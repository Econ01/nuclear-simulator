import numpy as np
from scipy.special import erf

# Constants
SEA_LEVEL_PRESSURE = 101.325  # kPa
GAMMA = 1.4  # Specific heat ratio for air
SPEED_OF_SOUND = 340.29  # m/s at sea level, 15°C
TNT_EQUIVALENCE = 4.184e12  # J/kt

def scaled_distance(yield_kt, distance_m, burst_height_m=0):
    """
    Calculate scaled distance (m/kg^1/3)
    Based on: Kingery, C.N. and Bulmash, G. (1984)
    """
    yield_kg = yield_kt * 1e6  # 1 kt = 10^6 kg TNT equivalent
    actual_distance = np.sqrt(distance_m**2 + burst_height_m**2)
    return actual_distance / (yield_kg ** (1/3))

def peak_overpressure(yield_kt, distance_m, burst_height_m=0):
    """
    Calculate peak overpressure in kPa using Kingery-Bulmash equations
    Reference: Technical Report ARBRL-TR-02555, US Army BRL
    """
    Z = scaled_distance(yield_kt, distance_m, burst_height_m)
    
    # Piecewise polynomial approximation
    if Z <= 0.035:
        return 6.7e4
    elif Z <= 0.1:
        logZ = np.log10(Z)
        logP = 4.54 - 3.10*logZ + 0.155*logZ**2
    elif Z <= 1.0:
        logZ = np.log10(Z)
        logP = 4.21 - 2.10*logZ - 0.340*logZ**2 + 0.066*logZ**3
    elif Z <= 10:
        logZ = np.log10(Z)
        logP = 3.71 - 0.920*logZ - 0.096*logZ**2 + 0.016*logZ**3
    else:
        logP = 1.5 - 1.85*np.log10(Z)
    
    P_psi = 10 ** logP
    return P_psi * 6.89476  # Convert to kPa

def dynamic_pressure(yield_kt, distance_m, burst_height_m=0):
    """
    Calculate dynamic pressure in kPa
    Based on: Glasstone and Dolan (1977)
    """
    P0 = SEA_LEVEL_PRESSURE / 6.89476  # Ambient pressure in psi
    P_psi = peak_overpressure(yield_kt, distance_m, burst_height_m) / 6.89476
    
    # For P_psi > 10 psi
    if P_psi > 10:
        q_psi = 2.5 * P_psi**2 / (P_psi + 7 * P0)
    else:
        # Brode's approximation for lower pressures
        q_psi = (5 * P_psi**2) / (2 * (P_psi + 7 * P0))
    
    return q_psi * 6.89476  # Convert to kPa

def arrival_time(yield_kt, distance_m, burst_height_m=0):
    """
    Calculate blast wave arrival time in seconds
    Based on: Dewey, J.M. (1964)
    """
    Z = scaled_distance(yield_kt, distance_m, burst_height_m)
    yield_kg = yield_kt * 1e6
    
    # Dewey's approximation
    if Z < 1.0:
        t_ms = 1.56 * (yield_kg**(1/3)) * Z * (1 + 0.019/Z**0.8)
    else:
        t_ms = 1.56 * (yield_kg**(1/3)) * Z * (1 + 0.029/Z**0.5)
    
    return t_ms * 0.001  # Convert to seconds

def positive_phase_duration(yield_kt, distance_m, burst_height_m=0):
    """
    Calculate positive phase duration in seconds
    Based on: Kinney and Graham (1985)
    """
    Z = scaled_distance(yield_kt, distance_m, burst_height_m)
    yield_kg = yield_kt * 1e6
    
    # Kinney-Graham approximation
    W = yield_kg
    R = distance_m
    H = burst_height_m
    
    if H == 0:  # Surface burst
        t_d = 1.35e-3 * np.sqrt(W) * (R / W**(1/3))**0.8
    else:  # Airburst
        slant_range = np.sqrt(R**2 + H**2)
        t_d = 1.65e-3 * W**(1/3) * (slant_range / W**(1/3))**0.6
    
    return t_d