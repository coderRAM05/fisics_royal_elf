import streamlit as st
import math

# --- 1. CORE UTILITY FUNCTIONS ---

def deg_to_dms(deg):
    """Converts decimal degrees to Degrees, Minutes, Seconds format."""
    if deg is None: return "N/A"
    sign = 1; deg = abs(deg)
    d = int(deg); m_float = (deg - d) * 60; m = int(m_float); s = (m_float - m) * 60
    return f"{sign * d}° {m}' {s:.2f}\""

def get_scale_factor(R_input, unit_name):
    """Adjusts the scale factor R for calculation and returns the unit symbol."""
    if "Angula" in unit_name: return R_input * 0.02, "m" 
    return R_input, unit_name.split()[0]

# --- 2. DIMENSION GENERATOR FUNCTIONS ---

def generate_yantra_data(lat_deg, lon_deg, R_input, unit_name):
    """Calculates all necessary dimensions and returns a dictionary of results."""
    
    # Constants
    OBLIQUITY_ECLIPTIC = 23.44
    IST_MERIDIAN = 82.5       

    scale_R_calc, unit_symbol = get_scale_factor(R_input, unit_name) 

    # Core Calculations
    phi_rad = math.radians(lat_deg)
    height_of_pole_angle = lat_deg
    colatitude_angle = 90.0 - lat_deg
    pala_bha_length = scale_R_calc * math.tan(phi_rad)
    time_correction_minutes = (lon_deg - IST_MERIDIAN) * 4

    # Samrat Yantra
    gnomon_angle = lat_deg 
    gnomon_base_length = scale_R_calc * math.cos(phi_rad)
    gnomon_vertical_height = scale_R_calc * math.sin(phi_rad)

    # Output Data Structure
    data = {
        # Summary
        "lat_dms": deg_to_dms(lat_deg),
        "lon_dms": deg_to_dms(lon_deg),
        "R_input": R_input,
        "unit": unit_name,
        "unit_symbol": unit_symbol,
        "colat_dms": deg_to_dms(colatitude_angle),
        "pala_bha": f"{pala_bha_length:.3f} {unit_symbol}",
        "time_corr_min": f"{time_correction_minutes:.2f}",
        "time_corr_desc": f"LST is {abs(time_correction_minutes):.2f} min {'ahead' if time_correction_minutes > 0 else 'behind'} IST",
        
        # Samrat Yantra
        "samrat_angle": deg_to_dms(gnomon_angle),
        "samrat_r": f"{scale_R_calc:.3f} {unit_symbol}",
        "samrat_base": f"{gnomon_base_length:.3f} {unit_symbol}",
        "samrat_height": f"{gnomon_vertical_height:.3f} {unit_symbol}",
        "samrat_declination_ex": f"{scale_R_calc * math.tan(math.radians(15)):.3f} {unit_symbol}",

        # Bhitti & Nadi Yantra
        "bhitti_r": f"{scale_R_calc:.3f} {unit_symbol}",
        "bhitti_pole_alt": deg_to_dms(height_of_pole_angle),
        "bhitti_equator_zd": deg_to_dms(colatitude_angle),
        "nadi_tilt": deg_to_dms(colatitude_angle),

        # Digamsa Yantra
        "digamsa_diameter": f"{2 * scale_R_calc:.3f} {unit_symbol}",
        "digamsa_pillar": f"{scale_R_calc / 5.0:.3f} {unit_symbol}",

        # Rama Yantra
        "rama_h": f"{scale_R_calc:.3f} {unit_symbol}",
        "rama_r": f"{scale_R_calc:.3f} {unit_symbol}",
        "rama_45deg": f"{scale_R_calc * math.tan(math.radians(45)):.3f} {unit_symbol}",

        # Rasivalaya Prep
        "epsilon": f"{OBLIQUITY_ECLIPTIC}°"
    }
    return data

# --- 3. STREAMLIT FRONT-END LAYOUT ---

st.set_page_config(layout="wide", page_title="Yantra Dimension Generator")

st.title(" प्राचीन वेधशाला यन्त्र (Ancient Observatory Yantra) Generator")
st.markdown("---")

# --- Input Sidebar ---
with st.sidebar:
    st.header("Site and Scale Input")
    
    # Input fields
    lat_deg = st.number_input("Latitude (Dec. Degrees N)", min_value=-90.0, max_value=90.0, value=26.91, step=0.01)
    lon_deg = st.number_input("Longitude (Dec. Degrees E)", min_value=-180.0, max_value=180.0, value=75.82, step=0.01)
    R_input = st.number_input("Scale Factor R (Input Value)", min_value=0.1, value=3.0, step=0.1)
    
    # Unit selection
    units = ["meters", "feet", "centimeters", "Angula (approx. 2cm)"]
    unit_name = st.selectbox("Output Unit", options=units)

    # Validation and Calculation
    if st.button("Generate Report", type="primary"):
        try:
            results = generate_yantra_data(lat_deg, lon_deg, R_input, unit_name)
            st.session_state['results'] = results
            st.success("Dimensions Calculated Successfully!")
        except Exception as e:
            st.error(f"Error during calculation: {e}")

# --- Output Main Page ---
if 'results' in st.session_state:
    data = st.session_state['results']
    st.header("Construction Report")
    
    # --- Tab Layout ---
    tab_sum, tab_samrat, tab_bhitti, tab_others = st.tabs([
        "Summary & Time", 
        "Samrat Yantra", 
        "Bhitti & Nadi Yantra", 
        "Rama, Digamsa, etc."
    ])

    # Utility function for report tables
    def display_details(tab, title, details):
        tab.subheader(title)
        report_data = [{"Dimension": k, "Value": v} for k, v in details]
        tab.table(report_data)

    # --- 1. Summary Tab ---
    with tab_sum:
        st.subheader("Site and Time Calibration")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Latitude (ϕ)", data['lat_dms'])
        col2.metric("Longitude (λ)", data['lon_dms'])
        col3.metric("Scale Factor (R)", f"{data['R_input']} {data['unit']}")

        st.markdown("---")
        st.subheader("Calibration Constants")
        colA, colB, colC = st.columns(3)
        colA.metric("Colatitude (90° - ϕ)", data['colat_dms'])
        colB.metric("Pala-bha (Equinox Shadow Length)", data['pala_bha'])
        colC.metric("Time Correction (vs IST)", data['time_corr_min'] + " min")
        st.info(f"**Alignment Note:** Local Solar Time (LST) is **{data['time_corr_desc']}**.")

    # --- 2. Samrat Yantra Tab ---
    with tab_samrat:
        display_details(tab_samrat, "Samrat Yantra (Equatorial Sundial)", [
            ("Gnomon Axis Angle (Slope to Horizontal)", data['samrat_angle']),
            ("Quadrant Radius (R)", data['samrat_r']),
            ("Gnomon Horizontal Base Length", data['samrat_base']),
            ("Gnomon Vertical Height at Base", data['samrat_height']),
            ("Alignment Note", "**True North-South** alignment is mandatory."),
        ])
        st.markdown(f"""
        <p><b>Declination Scale (Tangent Scale):</b> The distance (D) along the gnomon axis for declination δ is calculated as D = R × tan(δ).</p>
        <p>Example (15° Declination): {data['samrat_declination_ex']}</p>
        """, unsafe_allow_html=True)
        # 

    # --- 3. Bhitti & Nadi Yantra Tab ---
    with tab_bhitti:
        display_details(tab_bhitti, "Dakshinottara Bhitti Yantra (Meridian Arc)", [
            ("Arc Radius (R)", data['bhitti_r']),
            ("Critical Mark: Altitude of Celestial Pole (North)", data['bhitti_pole_alt']),
            ("Critical Mark: Zenith Distance of Equator (90° - ϕ)", data['bhitti_equator_zd']),
            ("Alignment Note", "Wall must be perfectly vertical and aligned **True North-South**."),
        ])
        
        display_details(tab_bhitti, "Nadi Valaya Yantra (Equatorial Ring Dial)", [
            ("Tilt Angle (Face to Horizontal)", data['nadi_tilt']),
            ("Alignment Note", "Gnomon axis must point **True North** (to the Celestial Pole)."),
        ])

    # --- 4. Other Yantras Tab ---
    with tab_others:
        display_details(tab_others, "Digamsa Yantra (Azimuth Instrument)", [
            ("Outer Circular Platform Diameter", data['digamsa_diameter']),
            ("Central Pillar Height (Recommended: R/5)", data['digamsa_pillar']),
            ("Scale", "**360°** graduated horizontal circle."),
            ("Alignment Note", "Base must be **Perfectly Level**. Zero mark must be **True North**."),
        ])
        
        display_details(tab_others, "Rama Yantra (Altitude & Azimuth Cylindrical)", [
            ("Central Pillar Height (H)", data['rama_h']),
            ("Outer Wall Radius (R)", data['rama_r']),
            ("Altitude (h) Scale Formula (Vertical, Z)", "Z = R × tan(h)"),
            ("Azimuth (A) Scale Formula (Horizontal, ρ)", "ρ = R × cos(h)"),
            ("Example (Altitude 45°)", f"Z = {data['rama_45deg']}"),
        ])
        
        st.subheader("Rāśivalaya Yantra (Ecliptic Coordinates)")
        st.info(f"**Preparation:** This complex instrument requires the **Obliquity of the Ecliptic ($\epsilon$)** ≈ {data['epsilon']}. Implementing the 12 unique tilts requires further spherical trigonometry.")