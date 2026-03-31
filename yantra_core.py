# yantra_core_v2.py  ─  Enhanced Calculation Engine
# Improvements over v1:
#   • Jai Prakash Yantra (6th instrument)
#   • Complete Rāśivalaya: all 12 zodiac tilt angles via spherical trig
#   • DMS output for every angular quantity
#   • Cleaner dict structure consumed by yantra_web_app_v2.py

import math

# ─── Constants ────────────────────────────────────────────────────────────────
OBLIQUITY_ECLIPTIC   = 23.44   # ε  – mean obliquity of the ecliptic (degrees)
IST_REFERENCE_LONG   = 82.5    # 82° 30' E  – Indian Standard Time meridian

RASHI_NAMES = [
    "Mesha (Aries)",       "Vrishabha (Taurus)",  "Mithuna (Gemini)",
    "Karka (Cancer)",      "Simha (Leo)",          "Kanya (Virgo)",
    "Tula (Libra)",        "Vrischika (Scorpio)",  "Dhanus (Sagittarius)",
    "Makara (Capricorn)",  "Kumbha (Aquarius)",    "Meena (Pisces)",
]

# ─── Utility ──────────────────────────────────────────────────────────────────
def decimal_to_dms(deg: float) -> str:
    """Convert decimal degrees → D° M' S.s\" string."""
    sign   = "-" if deg < 0 else ""
    deg    = abs(deg)
    d      = int(deg)
    m_f    = (deg - d) * 60
    m      = int(m_f)
    s      = (m_f - m) * 60
    return f"{sign}{d}° {m:02d}' {s:04.1f}\""


def _time_offset(lmbda: float):
    """LMT – IST offset.  Returns (formatted_str, offset_minutes)."""
    diff     = lmbda - IST_REFERENCE_LONG
    t_min    = diff * 4.0
    abs_sec  = abs(t_min) * 60
    h        = int(abs_sec // 3600)
    m        = int((abs_sec % 3600) // 60)
    s        = int(abs_sec % 60)
    direction = "AHEAD OF" if t_min >= 0 else "BEHIND"
    return f"{h:02d}h {m:02d}m {s:02d}s {direction} IST", t_min


# ─── Instrument calculators ───────────────────────────────────────────────────

def _samrat(phi: float, R: float) -> dict:
    """Samrat Yantra (Giant Equatorial Sundial)."""
    r = math.radians(phi)
    return {
        "angle_deg"  : phi,
        "angle_dms"  : decimal_to_dms(phi),
        "height"     : round(R * math.sin(r), 4),   # R·sin φ (vertical height of gnomon)
        "base"       : round(R * math.cos(r), 4),   # R·cos φ (horizontal base)
        "hypotenuse" : R,                            # = R by definition
        "decl_15deg" : round(R * math.tan(math.radians(15)), 4),  # sample declination scale mark
        "decl_23deg" : round(R * math.tan(math.radians(23.44)), 4),
    }


def _bhitti(phi: float, R: float) -> dict:
    """Dakshinottara Bhitti Yantra (Meridian Arc Wall)."""
    colat = 90.0 - phi
    return {
        "arc_radius"     : R,
        "pole_alt_deg"   : phi,
        "pole_alt_dms"   : decimal_to_dms(phi),
        "equator_zd_deg" : colat,
        "equator_zd_dms" : decimal_to_dms(colat),
    }


def _nadivalaya(phi: float, R: float) -> dict:
    """Nadi Valaya Yantra (Equatorial Ring/Disc)."""
    colat = 90.0 - phi
    return {
        "tilt_deg" : colat,
        "tilt_dms" : decimal_to_dms(colat),
        "radius"   : R,
    }


def _digamsa(phi: float, R: float) -> dict:
    """Digamsa Yantra (Azimuth Circle)."""
    return {
        "outer_diameter" : round(2 * R, 4),
        "pillar_height"  : round(R / 5.0, 4),
    }


def _rama(phi: float, R: float) -> dict:
    """Rama Yantra (Altitude-Azimuth Cylinder)."""
    alts = [15, 30, 45, 60, 75]
    vert_scale  = {f"{a}°": round(R * math.tan(math.radians(a)), 4) for a in alts}
    horiz_scale = {f"{a}°": round(R * math.cos(math.radians(a)), 4) for a in alts}
    return {
        "height"      : R,
        "radius"      : R,
        "vert_scale"  : vert_scale,   # Z = R·tan(h)
        "horiz_scale" : horiz_scale,  # ρ = R·cos(h)
    }


def _jai_prakash(phi: float, R: float) -> dict:
    """
    Jai Prakash Yantra (Hemispherical Bowl).
    ─────────────────────────────────────────
    A concave hemisphere sunk into the ground.
    The opening faces upward; the zenith is at the bowl's lowest point.
    Two complementary bowls (each with cross-shaped openings) form the pair.

    Key geometry:
      • Bowl radius  = R  (scale factor)
      • Bowl depth   = R  (full hemisphere)
      • Altitude circle for altitude h → projected radius from bowl-center = R·cos(h)
      • Azimuth is read directly off the rim (360° scale)
      • Shadow-casting wire spans N–S and E–W across the rim opening
    """
    phi_r  = math.radians(phi)
    colat  = 90.0 - phi

    # Distance on bowl floor (projected) from center to the equator crossing
    # The equator is at zenith-distance = 90°−φ  →  bowl-floor radius = R·cos(90°−φ) = R·sin(φ)
    pala_bha_bowl = round(R * math.sin(phi_r), 4)

    # Arc length along bowl surface from North rim to zenith-bottom
    # (arc subtends co-latitude angle at center)
    north_arc = round(R * math.radians(colat), 4)

    # Altitude scale marks: projected radial distance from bowl center (bottom)
    alt_marks = {
        f"{h}°": round(R * math.cos(math.radians(h)), 4)
        for h in [10, 20, 30, 45, 60, 75, 90]
    }

    return {
        "bowl_radius"      : round(R, 4),
        "bowl_depth"       : round(R, 4),            # hemisphere
        "bowl_diameter"    : round(2 * R, 4),
        "north_arc"        : north_arc,               # rim-north to zenith
        "pala_bha_bowl"    : pala_bha_bowl,           # equinox equator mark
        "alt_marks"        : alt_marks,               # altitude scale radii
        "meridian_wire"    : round(2 * R, 4),         # wire spans full diameter
        "equator_tilt_dms" : decimal_to_dms(colat),   # equator line tilt from horizontal
    }


def _rasivalaya(phi: float, R: float) -> list:
    """
    Rāśivalaya Yantras – 12 Ecliptic Instruments.
    ─────────────────────────────────────────────
    Each instrument is a small equatorial dial tilted so that its gnomon axis
    points to the ecliptic pole for that zodiac sign.  The tilt from horizontal
    equals the noon-altitude of the Sun at mid-sign:

        δ  = arcsin(sin ε · sin λ_mid)         [solar declination at mid-sign]
        tilt = (90° − φ) + δ  =  co-latitude + δ

    Reference: Nath (1983), Kaye (1918), Sharma (1995).
    """
    result = []
    for n in range(12):
        lam = n * 30 + 15   # mid-sign ecliptic longitude (degrees)

        # Solar declination at mid-sign
        delta = math.degrees(
            math.asin(math.sin(math.radians(OBLIQUITY_ECLIPTIC)) *
                      math.sin(math.radians(lam)))
        )

        tilt   = (90.0 - phi) + delta      # tilt from horizontal (= noon altitude)
        zd     = phi - delta               # zenith distance at noon

        result.append({
            "rashi"     : RASHI_NAMES[n],
            "n"         : n + 1,
            "lambda"    : lam,
            "delta_deg" : round(delta, 3),
            "delta_dms" : decimal_to_dms(delta),
            "tilt_deg"  : round(tilt, 3),
            "tilt_dms"  : decimal_to_dms(tilt),
            "zd_deg"    : round(zd, 3),
            "ring_diam" : round(R, 4),
        })
    return result


# ─── Master function ──────────────────────────────────────────────────────────

def calculate_all(latitude_phi: float, longitude_lambda: float, base_radius_R: float) -> dict:
    """
    Compute dimensions for all 7 Yantra types.

    Parameters
    ----------
    latitude_phi      : Site latitude in decimal degrees (0–90°N)
    longitude_lambda  : Site longitude in decimal degrees (0–180°E)
    base_radius_R     : Scale factor R in the chosen unit (e.g. metres)

    Returns
    -------
    dict  –  all angular and linear dimensions ready for display
    """
    phi = float(latitude_phi)
    lam = float(longitude_lambda)
    R   = float(base_radius_R)

    colat           = 90.0 - phi
    pala_bha        = round(R * math.tan(math.radians(phi)), 4)
    time_str, t_min = _time_offset(lam)

    return {
        # Site metadata
        "phi"       : phi,
        "lmbda"     : lam,
        "R"         : R,
        "phi_dms"   : decimal_to_dms(phi),
        "lmbda_dms" : decimal_to_dms(lam),
        "colat_deg" : colat,
        "colat_dms" : decimal_to_dms(colat),
        "pala_bha"  : pala_bha,

        # Time calibration
        "time_str"  : time_str,
        "time_min"  : t_min,
        "eot"       : {"Feb 11": -14.2, "May 14": +3.8, "Nov 03": +16.4},

        # Instrument data
        "samrat"     : _samrat(phi, R),
        "bhitti"     : _bhitti(phi, R),
        "nadivalaya" : _nadivalaya(phi, R),
        "digamsa"    : _digamsa(phi, R),
        "rama"       : _rama(phi, R),
        "jai_prakash": _jai_prakash(phi, R),
        "rasivalaya" : _rasivalaya(phi, R),
    }
