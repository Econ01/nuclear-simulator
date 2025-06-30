# backend/physics/models.py
import numpy as np
from scipy.special import erf

class NuclearBlastModel:
    """
    Implements open-source nuclear blast physics models based on:
    - Glasstone and Dolan (1977) - Effects of Nuclear Weapons
    - Kingery-Bulmash (1984) - Airblast Parameters
    - ORNL-TM-2020 (2021) - Modern Radiation Transport Models
    """
    
    # Constants
    ATMOSPHERIC_PRESSURE = 101.325  # kPa (sea level)
    SPEED_OF_SOUND = 343  # m/s (sea level, 20°C)
    FISSION_YIELD_FRACTION = 0.5  # Typical fission fraction for thermonuclear weapons
    
    @staticmethod
    def overpressure(yield_kt, distance_m, burst_height=0, surface_burst=False):
        """
        Calculate peak overpressure (kPa) using Kingery-Bulmash equations
        """
        # Scaled distance calculation
        scaled_distance = distance_m / (yield_kt ** (1/3))
        
        # Surface burst adjustment
        if surface_burst:
            scaled_distance *= 1.1  # Surface reflection factor
        
        # Kingery-Bulmash polynomial coefficients
        if scaled_distance < 1:
            p = 3.04e4 / scaled_distance + 1.13e3 / scaled_distance**2 - 0.57
        else:
            p = 1.9e3 / scaled_distance + 5.3e2 / scaled_distance**2 + 9.7e1 / scaled_distance**3
        
        return p * NuclearBlastModel.ATMOSPHERIC_PRESSURE

    @staticmethod
    def thermal_radiation(yield_kt, distance_m, visibility=10):
        """
        Calculate thermal radiation energy (cal/cm²) with atmospheric attenuation
        """
        # Basic inverse square law
        flux = (3000 * yield_kt) / (4 * np.pi * distance_m**2)
        
        # Atmospheric attenuation (Beer-Lambert law)
        attenuation = np.exp(-0.002 * distance_m / visibility)
        
        return flux * attenuation * 1e-4  # Convert to cal/cm²

    @staticmethod
    def radiation_dose(yield_kt, distance_m, time_after_explosion=1):
        """
        Calculate prompt radiation dose (Sieverts) with time decay
        """
        # Initial dose rate (Sv/s)
        initial_dose = 7.5e4 * yield_kt / distance_m**2
        
        # Time decay (t^-1.2 model)
        decay_factor = time_after_explosion ** -1.2
        
        return initial_dose * decay_factor

    @staticmethod
    def fallout_pattern(yield_kt, burst_height, wind_speed, wind_direction):
        """
        Calculate fallout distribution (simplified Gaussian plume model)
        Returns: (x, y) grid of contamination levels
        """
        # Fallout spread parameters
        sigma_x = wind_speed * 0.1 * yield_kt**0.5
        sigma_y = wind_speed * 0.05 * yield_kt**0.5
        
        # Create grid
        x = np.linspace(-5000, 5000, 100)
        y = np.linspace(-5000, 5000, 100)
        X, Y = np.meshgrid(x, y)
        
        # Rotate by wind direction
        theta = np.radians(wind_direction)
        Xr = X * np.cos(theta) - Y * np.sin(theta)
        Yr = X * np.sin(theta) + Y * np.cos(theta)
        
        # Gaussian distribution
        contamination = (yield_kt * 1e3 / (2 * np.pi * sigma_x * sigma_y) *  np.exp(-(Xr**2/(2 * sigma_x**2) + -(Yr**2/(2 * sigma_y**2)))))
        return X, Y, contamination