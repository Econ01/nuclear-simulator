import numpy as np

TNT_EQUIVALENCE = 4.184e12  # J/kt

def thermal_energy(yield_kt, distance_m, atmospheric_transmissivity=0.7, burst_height_m=0):
    """
    Calculate thermal radiation energy in cal/cm²
    Based on: Glasstone and Dolan (1977)
    """
    # Total thermal radiation energy (35-40% of total yield)
    thermal_fraction = 0.35
    thermal_energy_total = thermal_fraction * yield_kt * TNT_EQUIVALENCE  # Joules
    
    # Slant range for airbursts
    slant_range = np.sqrt(distance_m**2 + burst_height_m**2)
    
    # Energy per unit area (J/m²)
    energy_per_m2 = thermal_energy_total / (4 * np.pi * slant_range**2)
    
    # Convert to cal/cm² (1 cal = 4.184 J, 1 m² = 10,000 cm²)
    energy_cal_per_cm2 = energy_per_m2 / (4.184 * 10000)
    
    # Atmospheric attenuation
    return energy_cal_per_cm2 * atmospheric_transmissivity

def ignition_probability(thermal_energy, material="wood"):
    """
    Calculate ignition probability based on thermal energy
    Based on: DHS/OSTP 2010 report
    """
    if material == "wood":
        # Logistic function for wood ignition
        return 1 / (1 + np.exp(-0.1 * (thermal_energy - 15)))
    elif material == "fabric":
        return 1 / (1 + np.exp(-0.15 * (thermal_energy - 8)))
    else:  # General material
        return 1 / (1 + np.exp(-0.12 * (thermal_energy - 10)))