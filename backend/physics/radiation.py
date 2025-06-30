import numpy as np

def prompt_radiation_dose(yield_kt, distance_m, fission_fraction=0.5, burst_height_m=0):
    """
    Calculate prompt radiation dose in Sieverts
    Based on: NUREG/CR-4219 Rev. 2 (1990)
    """
    # Slant range for airbursts
    slant_range = np.sqrt(distance_m**2 + burst_height_m**2)
    
    # Neutron dose
    neutron_dose = 3.2e10 * fission_fraction * yield_kt / slant_range**2
    
    # Gamma dose
    gamma_dose = 8.7e10 * fission_fraction * yield_kt / slant_range**2
    
    # Total dose equivalent (neutrons have higher quality factor)
    total_sievert = neutron_dose * 10 * 1.602e-13 + gamma_dose * 1.602e-13
    return total_sievert

def residual_radiation_dose(yield_kt, distance_m, time_after_explosion, 
                           fission_fraction=0.5, wind_speed=5, rainout_factor=1.0):
    """
    Calculate fallout radiation dose rate in Sv/h
    Based on: NCRP Report No. 138 (2001)
    """
    # Scaling law for dose rate
    base_dose_rate = 1.0e4 * fission_fraction * yield_kt / (time_after_explosion**1.2)
    
    # Distance decay (1/r^2 law)
    distance_km = distance_m / 1000
    distance_factor = 1 / (distance_km**2) if distance_km > 0 else 1
    
    # Wind dispersion
    wind_factor = 1 / (1 + 0.1 * wind_speed)
    
    # Rainout enhancement
    rainout_factor = min(3.0, max(1.0, rainout_factor))
    
    return base_dose_rate * distance_factor * wind_factor * rainout_factor * 1e-6  # Convert to Sv/h