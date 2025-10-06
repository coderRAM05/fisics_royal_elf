import math

# --- Astronomical Constants ---
OBLIQUITY_ECLIPTIC = 23.44  # ε in degrees
IST_REFERENCE_LONGITUDE = 82.5  # 82° 30' E

def calculate_time_offset(longitude_lambda):
    """Calculates the constant difference between Local Mean Time (LMT) and IST."""
    longitude_difference = longitude_lambda - IST_REFERENCE_LONGITUDE
    time_offset_minutes = longitude_difference * 4
    
    abs_offset_seconds = abs(time_offset_minutes) * 60
    hours = int(abs_offset_seconds // 3600)
    minutes = int((abs_offset_seconds % 3600) // 60)
    seconds = int(abs_offset_seconds % 60)
    
    direction = "AHEAD OF" if time_offset_minutes > 0 else "BEHIND"
    
    return f"{hours:02d}h {minutes:02d}m {seconds:02d}s {direction} IST", time_offset_minutes

def calculate_yantra_dimensions(latitude_phi, longitude_lambda, base_radius_R):
    """Calculates all dimensional and calibration data for the Yantras."""
    
    phi = float(latitude_phi)
    lmbda = float(longitude_lambda)
    R = float(base_radius_R)

    phi_rad = math.radians(phi)
    
    # 1. Samrat Yantra
    samrat_gnomon_angle = phi
    samrat_gnomon_height = R * math.tan(phi_rad)
    
    # 2. Nadivalaya Yantra
    nadivalaya_tilt_angle = 90.0 - phi
    
    # 3. Daksinottara Bhitti (Alignment only)
    bhitti_alignment = "Must be aligned precisely North-South (Local Meridian)"
    
    # 4. Rasivalaya Yantras (Ecliptic tilt)
    ZD_eq = 90.0 - phi
    ZD_ss = ZD_eq - OBLIQUITY_ECLIPTIC # Min Zenith Distance (Summer Solstice)
    ZD_ws = ZD_eq + OBLIQUITY_ECLIPTIC # Max Zenith Distance (Winter Solstice)
    
    # 5. Time Calibration
    time_offset_str, time_offset_min = calculate_time_offset(lmbda)

    # Simplified EoT Chart (for illustrative calibration)
    eot_chart = {
        "Feb 11": -14.2, 
        "May 14": +3.8,
        "Nov 03": +16.4,
    }
    
    return {
        "phi": f"{phi:.4f}° N",
        "lmbda": f"{lmbda:.4f}° E",
        "R": f"{R:.3f}",
        "time_offset_str": time_offset_str,
        "time_offset_min": time_offset_min,
        
        "samrat_angle": f"{samrat_gnomon_angle:.3f}°",
        "samrat_height": f"{samrat_gnomon_height:.3f}",
        "nadivalaya_tilt": f"{nadivalaya_tilt_angle:.3f}°",
        "bhitti_alignment": bhitti_alignment,
        
        "rasivalaya_zd_ss": f"{ZD_ss:.3f}°",
        "rasivalaya_zd_ws": f"{ZD_ws:.3f}°",
        "eot_chart": eot_chart
    }