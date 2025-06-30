import numpy as np
from scipy.stats import multivariate_normal

def fallout_pattern(yield_kt, burst_height_m, latitude, longitude, 
                   wind_speed=5, wind_direction=90, resolution=100, radius=20000):
    """
    Calculate fallout distribution in kBq/m²
    Based on: NATO Handbook on the Medical Aspects of NBC Defensive Operations (1996)
    """
    # Create grid
    x = np.linspace(-radius, radius, resolution)
    y = np.linspace(-radius, resolution)
    X, Y = np.meshgrid(x, y)
    
    # Rotate coordinates by wind direction
    theta = np.radians(wind_direction)
    Xr = X * np.cos(theta) - Y * np.sin(theta)
    Yr = X * np.sin(theta) + Y * np.cos(theta)
    
    # Fallout parameters (simplified Gaussian plume model)
    activity_total = yield_kt * 1e15  # Total activity in Bq (1 kt ≈ 1e15 Bq)
    
    # Standard deviations based on wind speed and burst height
    sigma_x = 0.2 * wind_speed * (burst_height_m / 1000) * radius
    sigma_y = 0.1 * wind_speed * (burst_height_m / 1000) * radius
    
    # Prevent division by zero
    sigma_x = max(sigma_x, radius/100)
    sigma_y = max(sigma_y, radius/100)
    
    # Create 2D Gaussian distribution
    rv = multivariate_normal([0, 0], [[sigma_x**2, 0], [0, sigma_y**2]])
    pos = np.dstack((Xr, Yr))
    contamination = rv.pdf(pos)
    
    # Scale to total activity
    contamination = contamination / np.sum(contamination) * activity_total
    
    # Convert to kBq/m²
    contamination = contamination / 1000
    
    # Convert grid to geographic coordinates
    # 1 degree ≈ 111 km
    lon_grid = longitude + X / (111000 * np.cos(np.radians(latitude)))
    lat_grid = latitude + Y / 111000
    
    return lon_grid, lat_grid, contamination