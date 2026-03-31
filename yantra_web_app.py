# yantra_web_app_v2.py  ─  Enhanced Streamlit Front-End
# New in v2:
#   • Jai Prakash Yantra tab  (6th instrument)
#   • Complete Rāśivalaya: all 12 zodiac tilt angles + bar chart
#   • Dynamic Matplotlib diagrams: Samrat cross-section, Rāśivalaya tilt chart,
#     Jai Prakash bowl cross-section
#   • City presets including Pandharpur
#   • Downloadable text construction report

import math, io, sys, os, textwrap
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ─── Import core (handles both direct run and import) ─────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yantra_core_v2 import calculate_all, decimal_to_dms, RASHI_NAMES

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Yantra Dimension Generator v2",
    page_icon="🔭",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Source+Sans+3:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}

.stApp { background-color: #0d1117; color: #e6e6e6; }

/* ── Title ── */
.yg-hero {
    background: linear-gradient(135deg, #1a0a00 0%, #0d1117 60%);
    border-left: 4px solid #c9a227;
    border-radius: 6px;
    padding: 18px 24px 14px;
    margin-bottom: 12px;
}
.yg-title {
    font-family: 'Cinzel', serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #c9a227;
    margin: 0;
    letter-spacing: 0.04em;
}
.yg-subtitle {
    color: #8a8a9a;
    font-size: 0.85rem;
    margin-top: 4px;
    letter-spacing: 0.02em;
}

/* ── Metric cards ── */
.metric-strip {
    display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px;
}
.m-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px 16px;
    min-width: 130px;
}
.m-label { color: #7d8590; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; }
.m-value { color: #c9a227; font-size: 1.05rem; font-weight: 600; font-family: 'Cinzel', serif; }

/* ── Table style ── */
[data-testid="stDataFrame"] { border-radius: 6px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #21262d; }

/* ── Tabs ── */
[data-baseweb="tab-list"] { background: transparent; gap: 4px; }
[data-baseweb="tab"] {
    background: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 6px 6px 0 0 !important; color: #8a8a9a !important;
    font-size: 0.82rem;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #1a0a00 !important;
    border-color: #c9a227 !important;
    color: #c9a227 !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #c9a227, #8b6914) !important;
    color: #0d1117 !important; font-weight: 700 !important;
    border: none !important; border-radius: 6px !important;
}

/* ── Info/warning ── */
.stInfo, .stWarning { border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="yg-hero">
  <div class="yg-title">🔭 प्राचीन वेधशाला यन्त्र  ·  Yantra Dimension Generator  <span style="font-size:1rem;color:#8b6914">v2</span></div>
  <div class="yg-subtitle">
    Parametric engine for Jantar Mantar instruments &nbsp;|&nbsp;
    Samrat · Bhitti · Nadivalaya · Rama · Digamsa · Jai Prakash · Rāśivalaya (12 signs)
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Matplotlib helpers ───────────────────────────────────────────────────────
DARK_BG   = "#0d1117"
PANEL_BG  = "#161b22"
GOLD      = "#c9a227"
BLUE      = "#58a6ff"
RED       = "#f85149"
GREEN     = "#3fb950"
GRAY      = "#8b949e"


def _fig(w=8, h=5):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=DARK_BG)
    ax.set_facecolor(PANEL_BG)
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.tick_params(colors=GRAY)
    return fig, ax


def plot_samrat(d: dict):
    """Samrat Yantra gnomon cross-section (true proportions, north-facing)."""
    phi   = d["phi"]
    R     = d["R"]
    s     = d["samrat"]
    base  = s["base"]
    H     = s["height"]
    phi_r = math.radians(phi)

    fig, ax = _fig(8, 5)
    ax.axis("off")
    ax.set_title("Samrat Yantra — Gnomon Cross-Section (True North view)",
                 color=GRAY, fontsize=10, pad=8)

    # Ground line
    ax.plot([-0.25 * R, R * 1.35], [0, 0], color="#444", lw=1.5, ls="--")
    ax.text(R * 1.3, 0.02 * R, "Ground", color="#555", fontsize=8)

    # Gnomon triangle  O→(base,0)→(base,H)
    tx = [0, base, base, 0]
    ty = [0, 0,    H,    0]
    ax.fill(tx, ty, color=BLUE, alpha=0.18)
    ax.plot(tx, ty, color=BLUE, lw=2)

    # Hypotenuse label (mid-point)
    mid_x, mid_y = base / 2, H / 2
    ax.annotate(
        f"Hypotenuse = R = {R:.2f}",
        xy=(mid_x, mid_y),
        xytext=(mid_x - 0.38 * R, mid_y + 0.12 * R),
        color="white", fontsize=9,
        arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.8),
    )

    # φ angle arc
    theta = np.linspace(0, phi_r, 120)
    arc_r = 0.18 * R
    ax.plot(arc_r * np.cos(theta), arc_r * np.sin(theta), color=GOLD, lw=2)
    ax.text(0.21 * R, 0.04 * R, f"φ = {phi:.2f}°", color=GOLD, fontsize=10, fontweight="bold")

    # Height dimension
    ax.annotate("", xy=(base + 0.06 * R, H), xytext=(base + 0.06 * R, 0),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.2))
    ax.text(base + 0.09 * R, H / 2, f"H = {H:.3f}", color=RED, fontsize=9, va="center")

    # Base dimension
    ax.annotate("", xy=(base, -0.07 * R), xytext=(0, -0.07 * R),
                arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.2))
    ax.text(base / 2, -0.11 * R, f"Base = {base:.3f}", color=GREEN, fontsize=9, ha="center")

    # North pointer
    ax.annotate("▲ CELESTIAL NORTH POLE", xy=(0, H),
                xytext=(-0.22 * R, H * 0.82),
                color="#aaa", fontsize=8,
                arrowprops=dict(arrowstyle="->", color="#555", lw=0.8))

    ax.set_xlim(-0.35 * R, R * 1.5)
    ax.set_ylim(-0.2 * R, H * 1.3)
    ax.set_aspect("equal")
    plt.tight_layout()
    return fig


def plot_rasivalaya(d: dict):
    """Bar chart of all 12 Rāśivalaya tilt angles with colour-coded seasons."""
    rasi   = d["rasivalaya"]
    phi    = d["phi"]
    colat  = d["colat_deg"]

    labels = [r["rashi"].split(" ")[0] for r in rasi]
    tilts  = [r["tilt_deg"] for r in rasi]
    deltas = [r["delta_deg"] for r in rasi]
    colors = [RED if dlt >= 0 else BLUE for dlt in deltas]

    fig, ax = _fig(11, 5)
    x = np.arange(12)
    bars = ax.bar(x, tilts, 0.6, color=colors, alpha=0.82,
                  edgecolor="#30363d", linewidth=0.6)

    # Co-latitude reference line
    ax.axhline(y=colat, color=GOLD, ls="--", lw=1.5,
               label=f"Co-latitude = {colat:.1f}° (equinox tilt)")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=42, ha="right", color="white", fontsize=9)
    ax.set_ylabel("Tilt from Horizontal (°)", color=GRAY, fontsize=10)
    ax.set_title(
        f"Rāśivalaya Yantras — 12 Ecliptic Tilt Angles  (φ = {phi:.2f}°, ε = 23.44°)",
        color=GRAY, fontsize=11, pad=8,
    )
    ax.legend(
        handles=[
            mpatches.Patch(color=RED,  label="Sun north of equator (δ > 0)"),
            mpatches.Patch(color=BLUE, label="Sun south of equator (δ < 0)"),
            plt.Line2D([0], [0], color=GOLD, ls="--", label=f"Co-latitude = {colat:.1f}°"),
        ],
        facecolor=PANEL_BG, edgecolor="#30363d", labelcolor="white", fontsize=8,
    )

    # Tilt value on top of each bar
    for bar, t in zip(bars, tilts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.25,
                f"{t:.1f}°", ha="center", va="bottom", color="white", fontsize=7)

    plt.tight_layout()
    return fig


def plot_jai_prakash(d: dict):
    """Jai Prakash Yantra — hemispherical bowl cross-section."""
    phi = d["phi"]
    R   = d["R"]
    jp  = d["jai_prakash"]
    phi_r = math.radians(phi)

    fig, ax = _fig(6, 6)
    ax.axis("off")
    ax.set_title(
        f"Jai Prakash Yantra — Bowl Cross-Section  (φ = {phi:.2f}°)",
        color=GRAY, fontsize=10, pad=8,
    )

    # Hemispherical bowl (opening upward)
    theta   = np.linspace(0, np.pi, 300)
    bowl_x  =  R * np.cos(theta)
    bowl_y  = -R * np.sin(theta)

    ax.fill_between(bowl_x, bowl_y, 0, alpha=0.15, color=BLUE)
    ax.plot(bowl_x, bowl_y, color=BLUE, lw=2.5)

    # Rim
    ax.plot([-R, R], [0, 0], color="#555", lw=2)

    # Zenith dot (bowl bottom)
    ax.scatter([0], [-R], color=GOLD, s=90, zorder=6)
    ax.text(0.06 * R, -R + 0.03 * R, "Zenith", color=GOLD, fontsize=8)

    # Altitude circles projected onto cross-section
    for h_deg, clr in [(30, RED), (45, GREEN), (60, "#ff9f43")]:
        h_r      = math.radians(h_deg)
        rx       =  R * math.cos(h_r)
        ry       = -R * math.sin(h_r)
        ax.plot([-rx, rx], [ry, ry], color=clr, lw=0.8, ls=":", alpha=0.7)
        ax.scatter([ rx, -rx], [ry, ry], color=clr, s=28, zorder=5)
        ax.text(rx + 0.03 * R, ry + 0.02 * R, f"{h_deg}°", color=clr, fontsize=7)

    # Shadow wire
    ax.plot([-R * 0.96, R * 0.96], [0, 0],
            color="#ff9f43", lw=1.5, ls="--", alpha=0.9)
    ax.text(R * 0.5, 0.04 * R, "Shadow-casting wire (N–S)",
            color="#ff9f43", fontsize=7, ha="center")

    # Pala-bha mark
    pala = jp["pala_bha_bowl"]
    ax.scatter([0], [-pala], color=GREEN, s=70, zorder=6)
    ax.annotate(
        f"Pala-bha = {pala:.3f}\n(equator mark)",
        xy=(0, -pala), xytext=(0.22 * R, -pala - 0.1 * R),
        color=GREEN, fontsize=8,
        arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.8),
    )

    # Depth annotation
    ax.annotate("", xy=(R * 1.1, -R), xytext=(R * 1.1, 0),
                arrowprops=dict(arrowstyle="<->", color="white", lw=1))
    ax.text(R * 1.16, -R / 2, f"Depth\n= R = {R:.2f}", color="white", fontsize=8, va="center")

    ax.set_xlim(-R * 1.4, R * 1.65)
    ax.set_ylim(-R * 1.25, R * 0.3)
    ax.set_aspect("equal")
    plt.tight_layout()
    return fig


# ─── Text report ──────────────────────────────────────────────────────────────

def generate_report(d: dict, units: str) -> str:
    u  = units
    sp = d["samrat"]
    bh = d["bhitti"]
    nv = d["nadivalaya"]
    rm = d["rama"]
    dg = d["digamsa"]
    jp = d["jai_prakash"]
    ra = d["rasivalaya"]

    lines = [
        "=" * 66,
        "  YANTRA DIMENSION GENERATOR  —  CONSTRUCTION REPORT  (v2)",
        "=" * 66,
        f"  Latitude  (φ) : {d['phi_dms']}  ({d['phi']:.4f}°)",
        f"  Longitude (λ) : {d['lmbda_dms']}  ({d['lmbda']:.4f}°)",
        f"  Scale Factor  : R = {d['R']} {u}",
        f"  Co-latitude   : {d['colat_dms']}  ({d['colat_deg']:.3f}°)",
        f"  Pala-bha      : {d['pala_bha']} {u}  (equinox noon shadow = R·tan φ)",
        f"  LMT → IST     : {d['time_str']}",
        "",
        "─" * 66,
        "  I.  SAMRAT YANTRA  (Giant Equatorial Sundial)",
        "─" * 66,
        f"  Gnomon Axis Angle   = φ            : {sp['angle_dms']}",
        f"  Gnomon Height       = R·sin φ      : {sp['height']} {u}",
        f"  Gnomon Base         = R·cos φ      : {sp['base']} {u}",
        f"  Hypotenuse          = R             : {sp['hypotenuse']} {u}",
        f"  Declination mark 15°= R·tan(15°)   : {sp['decl_15deg']} {u}",
        f"  Declination mark ε  = R·tan(23.44°): {sp['decl_23deg']} {u}",
        "",
        "─" * 66,
        "  II.  DAKSHINOTTARA BHITTI YANTRA  (Meridian Arc Wall)",
        "─" * 66,
        f"  Arc Radius                 : {bh['arc_radius']} {u}",
        f"  Celestial Pole Mark        : {bh['pole_alt_dms']}",
        f"  Equator Zenith-Dist. Mark  : {bh['equator_zd_dms']}",
        "  Alignment                  : True North–South (local meridian)",
        "",
        "─" * 66,
        "  III.  NADI VALAYA YANTRA  (Equatorial Ring)",
        "─" * 66,
        f"  Disc Radius  : {nv['radius']} {u}",
        f"  Tilt Angle   : {nv['tilt_dms']}  (= co-latitude from horizontal)",
        "  Gnomon axis points True North toward Celestial Pole.",
        "",
        "─" * 66,
        "  IV.  RAMA YANTRA  (Altitude-Azimuth Cylinder)",
        "─" * 66,
        f"  Cylinder Height = R  : {rm['height']} {u}",
        f"  Cylinder Radius = R  : {rm['radius']} {u}",
        "  Vertical scale  Z  = R·tan(h)   |  Horizontal radius ρ = R·cos(h)",
    ]
    for alt, z in rm["vert_scale"].items():
        rho = rm["horiz_scale"][alt]
        lines.append(f"    Altitude {alt:>4} → Z = {z:8.4f} {u}   ρ = {rho:.4f} {u}")

    lines += [
        "",
        "─" * 66,
        "  V.  DIGAMSA YANTRA  (Azimuth Circle)",
        "─" * 66,
        f"  Platform Diameter     : {dg['outer_diameter']} {u}",
        f"  Central Pillar Height : {dg['pillar_height']} {u}",
        "  Scale                 : 360° graduated horizontal circle",
        "  Zero (0°) mark aligned to True North.",
        "",
        "─" * 66,
        "  VI.  JAI PRAKASH YANTRA  (Hemispherical Bowl)",
        "─" * 66,
        f"  Bowl Radius           : {jp['bowl_radius']} {u}",
        f"  Bowl Depth (= R)      : {jp['bowl_depth']} {u}",
        f"  Bowl Diameter         : {jp['bowl_diameter']} {u}",
        f"  N-Rim → Zenith Arc    : {jp['north_arc']} {u}  (arc length along bowl surface)",
        f"  Pala-bha on bowl floor: {jp['pala_bha_bowl']} {u}  (= R·sin φ)",
        f"  Shadow-casting wire   : {jp['meridian_wire']} {u}  (spans full diameter, N–S & E–W)",
        "  Altitude scale  (projected radial distance from bowl centre):",
    ]
    for h_label, r_val in jp["alt_marks"].items():
        lines.append(f"    h = {h_label:>4} → r = {r_val:.4f} {u}")

    lines += [
        "",
        "─" * 66,
        "  VII.  RĀŚIVALAYA YANTRAS  (12 Ecliptic Instruments)",
        "─" * 66,
        "  Tilt = co-latitude + δ  where δ = arcsin(sin 23.44° · sin λ_mid)",
        "",
        f"  {'Sign':<26}  {'λ_mid':>6}  {'δ':>8}  {'Tilt (DMS)':>20}  {'ZD':>8}",
        "  " + "─" * 62,
    ]
    for r in ra:
        lines.append(
            f"  {r['rashi']:<26}  {r['lambda']:>5}°  "
            f"{r['delta_deg']:>+7.2f}°  {r['tilt_dms']:>20}  {r['zd_deg']:>6.2f}°"
        )

    lines += [
        "",
        "─" * 66,
        "  VIII.  EQUATION OF TIME  (key correction points)",
        "─" * 66,
        "  Feb 11  →  ±14.2 min  (Sun at its fastest)",
        "  May 14  →  ±3.8  min",
        "  Nov 03  →  ±16.4 min  (Sun at its slowest)",
        "  True Solar Time = Yantra reading  ±  LMT-offset  ±  EoT (daily value)",
        "",
        "=" * 66,
        "  END OF REPORT",
        "=" * 66,
    ]
    return "\n".join(lines)


# ─── Sidebar ──────────────────────────────────────────────────────────────────

PRESETS = {
    "— Custom —"                        : None,
    "Jaipur        (26.91°N, 75.82°E)" : (26.91, 75.82),
    "Delhi         (28.62°N, 77.25°E)" : (28.62, 77.25),
    "Ujjain        (23.18°N, 75.77°E)" : (23.18, 75.77),
    "Varanasi      (25.31°N, 82.97°E)" : (25.31, 82.97),
    "Pandharpur    (17.68°N, 75.32°E)" : (17.68, 75.32),
}

with st.sidebar:
    st.markdown("### ⚙️ Site & Scale Input")

    preset = st.selectbox("Quick Preset Location", list(PRESETS.keys()))
    coords = PRESETS[preset]
    def_lat = coords[0] if coords else 26.91
    def_lon = coords[1] if coords else 75.82

    lat = st.number_input("Latitude φ (°N)", 0.0, 90.0,  float(def_lat), 0.01, "%.4f")
    lon = st.number_input("Longitude λ (°E)", 0.0, 180.0, float(def_lon), 0.01, "%.4f")
    R   = st.number_input("Scale Factor R", 0.1, value=10.0, step=0.5)
    u   = st.selectbox("Unit", ["meters", "feet", "centimeters"])

    st.markdown("---")
    run = st.button("🔭 Generate Report", type="primary", use_container_width=True)
    if run:
        if not (0 < lat < 90):
            st.error("Latitude must be between 0° and 90°.")
        else:
            try:
                st.session_state["d"]     = calculate_all(lat, lon, R)
                st.session_state["units"] = u
                st.success("✅ Dimensions calculated!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.caption("**Constants:** ε = 23.44°  |  IST = 82.5°E")
    st.caption("**References:** Kaye (1918), Sharma (1995), Surya Siddhanta")


# ─── Main Output ──────────────────────────────────────────────────────────────

if "d" not in st.session_state:
    st.markdown("### Getting started")
    c1, c2, c3 = st.columns(3)
    c1.info("**Step 1** – Choose a city preset or enter custom latitude / longitude.")
    c2.info("**Step 2** – Set your Scale Factor R (e.g. 10 meters).")
    c3.info("**Step 3** – Click **Generate Report** to compute all 7 instruments.")
    st.stop()

d = st.session_state["d"]
u = st.session_state["units"]

# ── Summary metric strip
cols = st.columns(5)
metrics = [
    ("Latitude φ",    d["phi_dms"]),
    ("Longitude λ",   d["lmbda_dms"]),
    (f"Scale R ({u})", str(d["R"])),
    ("Co-latitude",   d["colat_dms"]),
    ("Pala-bha",      f"{d['pala_bha']} {u}"),
]
for col, (lbl, val) in zip(cols, metrics):
    col.markdown(
        f'<div class="m-card"><div class="m-label">{lbl}</div>'
        f'<div class="m-value">{val}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Tabs
TABS = ["📊 Summary", "☀️ Samrat", "🧱 Bhitti & Nadi",
        "🌀 Rama & Digamsa", "🔵 Jai Prakash", "♈ Rāśivalaya", "📄 Report"]
tabs = st.tabs(TABS)

# ───────────────────────────────────────────────────────────────────────────────
# Tab 0 – Summary
# ───────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Core Geometric Constants")
        st.markdown(f"""
| Constant | Formula | Value |
|---|---|---|
| Gnomon Angle | φ | **{d['phi_dms']}** |
| Co-latitude | 90° − φ | **{d['colat_dms']}** |
| Pala-bha (equinox shadow) | R · tan φ | **{d['pala_bha']} {u}** |
| Obliquity of Ecliptic ε | (constant) | 23.44° |
| IST Reference Meridian | (constant) | 82.5° E |
""")

    with c2:
        st.subheader("Time Calibration")
        direction = "ahead of" if d["time_min"] > 0 else "behind"
        st.markdown(f"""
| Parameter | Value |
|---|---|
| LMT to IST Offset | `{d['time_str']}` |
| EoT — Feb 11 | ±14.2 min  (Sun fastest) |
| EoT — May 14 | ±3.8 min |
| EoT — Nov 03 | ±16.4 min  (Sun slowest) |
""")
        st.info(
            f"Local Mean Time at this site is **{abs(d['time_min']):.2f} min "
            f"{direction} IST**.  "
            f"Final corrected time = LMT ± EoT (daily value)."
        )

# ───────────────────────────────────────────────────────────────────────────────
# Tab 1 – Samrat Yantra
# ───────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    c1, c2 = st.columns([1, 1])
    sp = d["samrat"]
    with c1:
        st.subheader("Samrat Yantra Dimensions")
        st.markdown(f"""
| Dimension | Formula | Value |
|---|---|---|
| Gnomon Axis Angle | φ | **{sp['angle_dms']}** |
| Gnomon Height | R · sin φ | **{sp['height']} {u}** |
| Gnomon Base | R · cos φ | **{sp['base']} {u}** |
| Hypotenuse | R | **{d['R']} {u}** |
| Decl. scale mark (15°) | R · tan 15° | {sp['decl_15deg']} {u} |
| Decl. scale mark (ε=23.44°) | R · tan ε | {sp['decl_23deg']} {u} |
""")
        st.warning("🧭 Hypotenuse **must** point True North toward the Celestial Pole.")
    with c2:
        with st.spinner("Drawing diagram…"):
            fig = plot_samrat(d)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

# ───────────────────────────────────────────────────────────────────────────────
# Tab 2 – Bhitti & Nadi
# ───────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    c1, c2 = st.columns(2)
    bh = d["bhitti"]
    nv = d["nadivalaya"]

    with c1:
        st.subheader("Dakshinottara Bhitti Yantra")
        st.markdown(f"""
| Dimension | Value |
|---|---|
| Arc Radius (R) | **{bh['arc_radius']} {u}** |
| Celestial Pole Mark | **{bh['pole_alt_dms']}** |
| Equator Zenith-Distance Mark | **{bh['equator_zd_dms']}** |
| Wall alignment | **True North–South** |
""")
        st.info("The pole-altitude mark and the equator ZD mark are the two critical calibration points engraved on the arc.")

    with c2:
        st.subheader("Nadi Valaya Yantra  (Equatorial Ring Dial)")
        st.markdown(f"""
| Dimension | Value |
|---|---|
| Disc Radius | **{nv['radius']} {u}** |
| Tilt from Horizontal | **{nv['tilt_dms']}** |
| Gnomon direction | **True North (Celestial Pole)** |
""")
        st.info(f"Tilt = Co-latitude = 90° − φ = {d['colat_dms']}")

# ───────────────────────────────────────────────────────────────────────────────
# Tab 3 – Rama & Digamsa
# ───────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    c1, c2 = st.columns(2)
    rm = d["rama"]
    dg = d["digamsa"]

    with c1:
        st.subheader("Rama Yantra  (Altitude-Azimuth Cylinder)")
        st.markdown(f"""
| Dimension | Formula | Value |
|---|---|---|
| Cylinder Height | R | **{rm['height']} {u}** |
| Cylinder Radius | R | **{rm['radius']} {u}** |
""")
        scale_rows = [
            {"Altitude h": k,
             f"Vertical Z = R·tan(h)  [{u}]": v,
             f"Horiz. ρ = R·cos(h)  [{u}]": rm["horiz_scale"][k]}
            for k, v in rm["vert_scale"].items()
        ]
        st.dataframe(scale_rows, hide_index=True, use_container_width=True)
        st.caption("Z gives the height mark on the inner wall; ρ gives the radial mark on the floor.")

    with c2:
        st.subheader("Digamsa Yantra  (Azimuth Circle)")
        st.markdown(f"""
| Dimension | Formula | Value |
|---|---|---|
| Platform Diameter | 2R | **{dg['outer_diameter']} {u}** |
| Central Pillar Height | R / 5 | **{dg['pillar_height']} {u}** |
| Azimuth Scale | — | **360° graduated** |
""")
        st.warning("🧭 Zero mark must be aligned to True North. Platform must be perfectly level.")

# ───────────────────────────────────────────────────────────────────────────────
# Tab 4 – Jai Prakash Yantra  ← NEW
# ───────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    c1, c2 = st.columns([1, 1])
    jp = d["jai_prakash"]

    with c1:
        st.subheader("Jai Prakash Yantra  (Hemispherical Bowl)")
        st.markdown(f"""
| Dimension | Formula | Value |
|---|---|---|
| Bowl Radius | R | **{jp['bowl_radius']} {u}** |
| Bowl Depth | R (hemisphere) | **{jp['bowl_depth']} {u}** |
| Bowl Diameter | 2R | **{jp['bowl_diameter']} {u}** |
| N-Rim → Zenith arc | R · (co-lat)ₐₐᵣ | **{jp['north_arc']} {u}** |
| Pala-bha on floor | R · sin φ | **{jp['pala_bha_bowl']} {u}** |
| Shadow wire length | 2R | **{jp['meridian_wire']} {u}** |
""")
        st.subheader("Altitude Scale Marks")
        alt_rows = [{"Altitude h": h, f"Radial distance from centre [{u}]": r}
                    for h, r in jp["alt_marks"].items()]
        st.dataframe(alt_rows, hide_index=True, use_container_width=True)
        st.info(
            "Two complementary bowls (each with a cross-shaped opening) form the complete "
            "instrument.  Shadow-casting wires span N–S and E–W across the open top.  "
            "Altitude mark formula: r = R · cos(h)."
        )

    with c2:
        with st.spinner("Drawing bowl diagram…"):
            fig = plot_jai_prakash(d)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

# ───────────────────────────────────────────────────────────────────────────────
# Tab 5 – Rāśivalaya  ← COMPLETED
# ───────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("Rāśivalaya Yantras — All 12 Ecliptic Instruments")
    st.caption(
        f"φ = {d['phi']:.4f}°  |  ε = 23.44°  |  "
        "Tilt = (90° − φ) + δ,  where  δ = arcsin(sin ε · sin λ_mid)"
    )

    rasi_rows = [
        {
            "Rāshi (Sign)"         : r["rashi"],
            "λ_mid (°)"           : r["lambda"],
            "Declination δ"        : f"{r['delta_deg']:+.2f}°",
            "Tilt from Horizontal" : r["tilt_dms"],
            "Zenith Distance"      : f"{r['zd_deg']:.2f}°",
            "Ring Diameter"        : f"{r['ring_diam']} {u}",
        }
        for r in d["rasivalaya"]
    ]
    st.dataframe(rasi_rows, hide_index=True, use_container_width=True)

    with st.spinner("Drawing Rāśivalaya tilt chart…"):
        fig = plot_rasivalaya(d)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.info(
        "Red bars: Sun north of celestial equator (δ > 0) — summer signs.  "
        "Blue bars: Sun south of equator (δ < 0) — winter signs.  "
        "The gold dashed line marks the equinox reference (co-latitude = tilt when δ = 0)."
    )

# ───────────────────────────────────────────────────────────────────────────────
# Tab 6 – Downloadable Report
# ───────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.subheader("📄 Full Construction Report")
    report = generate_report(d, u)
    st.code(report, language=None)
    st.download_button(
        label="⬇️ Download Report (.txt)",
        data=report,
        file_name=f"yantra_report_phi{d['phi']:.2f}_R{d['R']}.txt",
        mime="text/plain",
        use_container_width=True,
    )
