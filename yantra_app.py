# yantra_app.py
from jinja2 import Environment, FileSystemLoader
# Assuming yantra_core.py is in the same directory and contains the calculation function
from yantra_core import calculate_yantra_dimensions
import io # Necessary for reliable file writing with encoding

# Template for the output report (This is the clean text report for console)
REPORT_TEMPLATE = """
===================================================
      ANCIENT YANTRA DIMENSION GENERATOR REPORT 
===================================================

SITE & SCALE SPECIFICATIONS
-----------------------------------
- Latitude (\u03C6):       {{ data.phi }}
- Longitude (\u03BB):      {{ data.lmbda }}
- Base Scale Radius (R): {{ data.R }} Units (e.g., Meters)
- True North Alignment:  0.00\u00B0 Azimuth (Mandatory for all Yantras)

===================================================
I. DIMENSIONAL DATA (Latitude \u03C6 Dependent)
===================================================

1. SAMRAT YANTRA (Giant Equinoctial Sundial)
-----------------------------------
- Gnomon Angle (\u03C6):   {{ data.samrat_angle }}
  * This is the angle the shadow-casting hypotenuse must make with the horizontal base.
- Gnomon Height (H):    {{ data.samrat_height }} Units
  * Calculated as H = R * tan(\u03C6).

2. NADIVALAYA YANTRA (Equatorial Disc)
-----------------------------------
- Disc Tilt Angle:      {{ data.nadivalaya_tilt }}
  * This is the angle the equatorial plane (disc) is tilted up from the horizontal.
- Disc Radius (R): **{{ data.R }} Units**
  * The physical radius of the disc should match the Base Scale R.

3. DAKSINOTTARA BHITTI YANTRA (Meridian Wall)
-----------------------------------
- Wall Alignment:       {{ data.bhitti_alignment }}
  * The wall must be constructed exactly North-South.
- Arc Radius (R): **{{ data.R }} Units**
  * The radius of the embedded arc should match the Base Scale R for consistency.

4. RASIVALAYA YANTRAS (Ecliptic Rings)
-----------------------------------
- The structure's tilt is determined by the Ecliptic plane's geometry:
  - Max Zenith Distance (Winter Solstice): {{ data.rasivalaya_zd_ws }}
  - Min Zenith Distance (Summer Solstice): {{ data.rasivalaya_zd_ss }}
- Ring Diameter: **{{ data.R }} Units**
  * The diameter of the 12 masonry rings is set proportionally to the Base Scale R.
===================================================
II. CALIBRATION DATA (Longitude \u03BB Dependent)
===================================================

- LMT to IST Offset:    {{ data.time_offset_str }}
  * Local Mean Time (LMT) measured by the Yantra is this amount {{ "ahead of" if data.time_offset_min > 0 else "behind" }} Indian Standard Time (IST).

- Equation of Time (EoT) Key Points:
  * Feb 11: {{ data.eot_chart['Feb 11'] }}\u00B1 min (Fastest Sun)
  * May 14: {{ data.eot_chart['May 14'] }}\u00B1 min
  * Nov 03: {{ data.eot_chart['Nov 03'] }}\u00B1 min (Slowest Sun)
  * Note: The final time reading must be corrected by LMT Offset AND the daily EoT.

===================================================
REPORT END.
===================================================
"""
# yantra_app.py (Replace the existing main() function)
def main():
    """Main application loop to gather input and generate the report."""
    
    print("\n--- WELCOME TO YANTRA DIMENSION GENERATOR ---")
    print("Please enter the required geographical data for the construction site.")
    
    try:
        # User Input
        # NOTE: .strip() is added for better input handling (removes accidental spaces)
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
    # Assuming calculate_yantra_dimensions is imported from yantra_core.py
    data = calculate_yantra_dimensions(latitude, longitude, base_radius)
    
    # 2. Render the report
    env = Environment(loader=FileSystemLoader('.'))
    template = env.from_string(REPORT_TEMPLATE)
    
    # 3. DIRECTLY PRINT THE OUTPUT TO THE CONSOLE
    report_output = template.render(data=data)
    
    print("\n" + "="*50)
    print("      *** GENERATED YANTRA CONSTRUCTION REPORT ***")
    print("="*50)
    print(report_output)
    print("="*50)

if __name__ == "__main__":
    main()