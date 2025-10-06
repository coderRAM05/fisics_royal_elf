import math
import sys
from jinja2 import Environment

# --- Configuration & Constants ---
OBLIQUITY_ECLIPTIC = 23.44  # Obliquity of the Ecliptic (ε)
IST_REFERENCE_LONGITUDE = 82.5  # 82° 30' E

# --- CORE LOGIC ---

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
    ZD_ss = ZD_eq - OBLIQUITY_ECLIPTIC 
    ZD_ws = ZD_eq + OBLIQUITY_ECLIPTIC
    
    # 5. Time Calibration
    time_offset_str, time_offset_min = calculate_time_offset(lmbda)

    # Simplified EoT Chart
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

# --- REPORT TEMPLATE (Designed for console output) ---

REPORT_TEMPLATE = """
===================================================
      ANCIENT YANTRA DIMENSION GENERATOR REPORT 
===================================================

SITE & SCALE SPECIFICATIONS
-----------------------------------
- Latitude (φ):       {{ data.phi }}
- Longitude (λ):      {{ data.lmbda }}
- Base Scale Radius (R): {{ data.R }} Units (e.g., Meters)
- True North Alignment:  0.00° Azimuth (Mandatory for all Yantras)

===================================================
I. DIMENSIONAL DATA (Latitude φ Dependent)
===================================================

1. SAMRAT YANTRA (Giant Equinoctial Sundial)
-----------------------------------
- Gnomon Angle (φ):   {{ data.samrat_angle }}
  * This is the angle the shadow-casting hypotenuse must make with the horizontal base.
- Gnomon Height (H):    {{ data.samrat_height }} Units
  * Calculated as H = R * tan(φ).

2. NADIVALAYA YANTRA (Equatorial Disc)
-----------------------------------
- Disc Tilt Angle:      {{ data.nadivalaya_tilt }}
  * This is the angle the equatorial plane (disc) is tilted up from the horizontal.
- Disc Radius (R): {{ data.R }} Units
  * The physical radius of the disc should match the Base Scale R.

3. DAKSINOTTARA BHITTI YANTRA (Meridian Wall)
-----------------------------------
- Wall Alignment:       {{ data.bhitti_alignment }}
  * The wall must be constructed exactly North-South.
- Arc Radius (R): {{ data.R }} Units
  * The radius of the embedded arc should match the Base Scale R for consistency.

4. RASIVALAYA YANTRAS (Ecliptic Rings)
-----------------------------------
- The structure's tilt is determined by the Ecliptic plane's geometry:
  - Max Zenith Distance (Winter Solstice): {{ data.rasivalaya_zd_ws }}
  - Min Zenith Distance (Summer Solstice): {{ data.rasivalaya_zd_ss }}
- Ring Diameter: {{ data.R }} Units
  * The diameter of the 12 masonry rings is set proportionally to the Base Scale R.
===================================================
II. CALIBRATION DATA (Longitude λ Dependent)
===================================================

- LMT to IST Offset:    {{ data.time_offset_str }}
  * Local Mean Time (LMT) measured by the Yantra is this amount {{ "ahead of" if data.time_offset_min > 0 else "behind" }} Indian Standard Time (IST).

- Equation of Time (EoT) Key Points:
  * Feb 11: {{ data.eot_chart['Feb 11'] }}± min (Fastest Sun)
  * May 14: {{ data.eot_chart['May 14'] }}± min
  * Nov 03: {{ data.eot_chart['Nov 03'] }}± min (Slowest Sun)
  * Note: The final time reading must be corrected by LMT Offset AND the daily EoT.

===================================================
REPORT END.
===================================================
"""

# --- Main Execution Block ---

def main():
    """Main application loop to gather input and generate the report."""
    
    try:
        # Check for Jinja2 before proceeding
        from jinja2 import Environment
    except ImportError:
        print("\nERROR: The 'jinja2' library is required to run this application.")
        print("Please install it using the command: pip install Jinja2")
        sys.exit(1)

    print("\n--- WELCOME TO YANTRA DIMENSION GENERATOR ---")
    print("Please enter the required geographical data for the construction site.")
    
    try:
        # User Input (using .strip() for robust input handling)
        latitude = float(input("Enter Latitude (e.g., 26.9167 for Jaipur): ").strip())
        longitude = float(input("Enter Longitude (e.g., 75.8167 for Jaipur): ").strip())
        base_radius = float(input("Enter Base Scale Radius (R, e.g., 10.0 meters): ").strip())
        
        if not (0 <= latitude <= 90): raise ValueError("Latitude must be between 0 and 90.")
        if not (0 <= longitude <= 180): raise ValueError("Longitude must be between 0 and 180 (East).")
        if base_radius <= 0: raise ValueError("Radius must be positive.")

    except ValueError as e:
        print(f"\nERROR: Invalid input. {e}")
        return

    # 1. Calculate the dimensions
    data = calculate_yantra_dimensions(latitude, longitude, base_radius)
    
    # 2. Render the report directly to the console
    # The loader is set to None since the template is a string in this file
    env = Environment(loader=None) 
    template = env.from_string(REPORT_TEMPLATE)
    
    report_output = template.render(data=data)
    
    # Print the final report
    #print("\n" + "="*50)
   #print("      *** GENERATED YANTRA CONSTRUCTION REPORT ***")
    #print("="*50)
    print(report_output)
    #print("="*50)
    print("\nThank you for using the Yantra Generator.")


if __name__ == "__main__":
    main()