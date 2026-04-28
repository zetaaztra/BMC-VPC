import streamlit as st
import json
import csv
import io
import os
import math
from datetime import datetime

# ── OPTIONAL: Plotly for premium charts ──────────────────────
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Canvas Studio Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME TOKENS ──────────────────────────────────────────────
DARK = {
    "bg0": "#0c0c14", "bg1": "#13131f", "bg2": "#1a1a2e", "bg3": "#22223a",
    "glass": "rgba(26,26,46,0.65)", "glass2": "rgba(30,30,50,0.45)",
    "border": "#2a2a45", "border2": "#3d3d5f",
    "text": "#f0f0fa", "text2": "#a0a0c8", "text3": "#55557a",
    "a1": "#00d4aa", "a2": "#ff6b35", "a3": "#6c7fff", "a4": "#f7c948",
    "a5": "#ff4785", "a6": "#00d4ff",
    "red": "#e05252", "green": "#3ecf8e",
    "shadow": "0 12px 48px rgba(0,0,0,0.60)",
    "shadow_sm": "0 4px 16px rgba(0,0,0,0.40)",
    "card_bg": "#1a1a2e", "hero_grad": "135deg,#1a1a2e 0%,#13131f 40%,#0c0c14 100%",
    "mesh1": "rgba(0,212,170,0.12)", "mesh2": "rgba(108,127,255,0.10)", "mesh3": "rgba(255,71,133,0.08)",
    "input_bg": "#1a1a2e", "label_color": "#a0a0c8",
    "ibanner_bg": "rgba(108,127,255,0.08)", "ibanner_border": "rgba(108,127,255,0.25)",
    "tip_bg": "rgba(0,212,170,0.07)", "tip_border": "rgba(0,212,170,0.22)",
    "neon_teal": "0 0 20px rgba(0,212,170,0.25), 0 0 60px rgba(0,212,170,0.10)",
    "neon_orange": "0 0 20px rgba(255,107,53,0.25), 0 0 60px rgba(255,107,53,0.10)",
    "neon_indigo": "0 0 20px rgba(108,127,255,0.25), 0 0 60px rgba(108,127,255,0.10)",
    "glow_teal": "rgba(0,212,170,0.4)",
    "mode_name": "🌙 DARK",
}

LIGHT = {
    "bg0": "#f0f2fa", "bg1": "#ffffff", "bg2": "#f5f7ff", "bg3": "#e8ecf8",
    "glass": "rgba(255,255,255,0.72)", "glass2": "rgba(245,247,255,0.55)",
    "border": "#d8dcee", "border2": "#c0c8e8",
    "text": "#12122a", "text2": "#3d3d6a", "text3": "#8888b0",
    "a1": "#007a63", "a2": "#c84a00", "a3": "#3040c8", "a4": "#a87800",
    "a5": "#c4184f", "a6": "#0078a3",
    "red": "#b52828", "green": "#1a7040",
    "shadow": "0 8px 32px rgba(0,0,0,0.10)",
    "shadow_sm": "0 2px 8px rgba(0,0,0,0.06)",
    "card_bg": "#ffffff", "hero_grad": "135deg,#ffffff 0%,#f5f7ff 50%,#f0f2fa 100%",
    "mesh1": "rgba(0,122,99,0.08)", "mesh2": "rgba(48,64,200,0.07)", "mesh3": "rgba(196,24,79,0.06)",
    "input_bg": "#f5f7ff", "label_color": "#3d3d6a",
    "ibanner_bg": "rgba(48,64,200,0.06)", "ibanner_border": "rgba(48,64,200,0.20)",
    "tip_bg": "rgba(0,122,99,0.06)", "tip_border": "rgba(0,122,99,0.22)",
    "neon_teal": "0 4px 16px rgba(0,122,99,0.12)",
    "neon_orange": "0 4px 16px rgba(200,74,0,0.12)",
    "neon_indigo": "0 4px 16px rgba(48,64,200,0.12)",
    "glow_teal": "rgba(0,122,99,0.2)",
    "mode_name": "☀️ LIGHT",
}

def init():
    ALL_FIELDS = [
        "key_partners", "key_activities", "value_propositions",
        "customer_relationships", "customer_segments", "key_resources",
        "channels", "cost_structure", "revenue_streams",
        "customer_jobs", "customer_pains", "customer_gains",
        "products_services", "pain_relievers", "gain_creators",
        "swot_s", "swot_w", "swot_o", "swot_t",
        "rev_price", "rev_volume", "rev_fixed_cost", "rev_var_cost"
    ]
    if "canvas" not in st.session_state:
        st.session_state.canvas = {f: "" for f in ALL_FIELDS}
    if "history" not in st.session_state:
        st.session_state.history = []
    if "file_name" not in st.session_state:
        st.session_state.file_name = "my_startup_canvas"
    if "founder_name" not in st.session_state:
        st.session_state.founder_name = ""
    if "company_name" not in st.session_state:
        st.session_state.company_name = ""
    if "saved_files" not in st.session_state:
        st.session_state.saved_files = {}
    if "active_file" not in st.session_state:
        st.session_state.active_file = None
    if "show_tips" not in st.session_state:
        st.session_state.show_tips = True
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    if "last_saved" not in st.session_state:
        st.session_state.last_saved = None
    if "hypotheses" not in st.session_state:
        st.session_state.hypotheses = []
    # Patch existing session state if fields are missing
    for f in ALL_FIELDS:
        if f not in st.session_state.canvas:
            st.session_state.canvas[f] = ""

init()
T = DARK if st.session_state.theme == "dark" else LIGHT

# ── CSS INJECTION ────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600;700&display=swap');

:root {{
  --bg0:{T['bg0']};--bg1:{T['bg1']};--bg2:{T['bg2']};--bg3:{T['bg3']};
  --glass:{T['glass']};--glass2:{T['glass2']};
  --border:{T['border']};--border2:{T['border2']};
  --text:{T['text']};--text2:{T['text2']};--text3:{T['text3']};
  --a1:{T['a1']};--a2:{T['a2']};--a3:{T['a3']};--a4:{T['a4']};--a5:{T['a5']};--a6:{T['a6']};
  --red:{T['red']};--green:{T['green']};
  --shadow:{T['shadow']};--shadow_sm:{T['shadow_sm']};
  --card:{T['card_bg']};--ibg:{T['input_bg']};--lc:{T['label_color']};
  --glow_teal:{T['glow_teal']};
}}

html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{{
  background:var(--bg0)!important;
  font-family:'Outfit','Inter',sans-serif!important;
  color:var(--text);
  font-size:18px;
}}

/* Animated gradient mesh background */
[data-testid="stAppViewContainer"]::before {{
  content:'';position:fixed;top:0;left:0;right:0;bottom:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 600px 400px at 10% 20%, {T['mesh1']}, transparent),
    radial-gradient(ellipse 500px 500px at 80% 30%, {T['mesh2']}, transparent),
    radial-gradient(ellipse 400px 300px at 50% 80%, {T['mesh3']}, transparent);
  animation:meshShift 12s ease-in-out infinite alternate;
}}
@keyframes meshShift {{
  0%{{transform:translate(0,0) scale(1);}}
  50%{{transform:translate(30px,-20px) scale(1.05);}}
  100%{{transform:translate(-20px,10px) scale(1);}}
}}

/* Particle effect overlay */
[data-testid="stAppViewContainer"]::after {{
  content:'';position:fixed;top:0;left:0;right:0;bottom:0;z-index:1;pointer-events:none;
  background-image:
    radial-gradient(circle 2px at 15% 25%, {T['a1']}40 0%, transparent 100%),
    radial-gradient(circle 1.5px at 75% 15%, {T['a3']}30 0%, transparent 100%),
    radial-gradient(circle 2.5px at 45% 65%, {T['a2']}25 0%, transparent 100%),
    radial-gradient(circle 1px at 85% 75%, {T['a4']}20 0%, transparent 100%),
    radial-gradient(circle 2px at 25% 85%, {T['a5']}20 0%, transparent 100%);
  animation:particleFloat 20s linear infinite;
}}
@keyframes particleFloat {{
  0%{{transform:translateY(0px) translateX(0px);}}
  25%{{transform:translateY(-15px) translateX(8px);}}
  50%{{transform:translateY(-8px) translateX(-5px);}}
  75%{{transform:translateY(5px) translateX(12px);}}
  100%{{transform:translateY(0px) translateX(0px);}}
}}

::-webkit-scrollbar{{width:7px;height:7px}}
::-webkit-scrollbar-track{{background:var(--bg1)}}
::-webkit-scrollbar-thumb{{background:var(--border2);border-radius:4px}}

/* ── GLASSMORPHISM SIDEBAR ── */
[data-testid="stSidebar"]{{
  background:linear-gradient(180deg,{T['glass']},{T['glass2']})!important;
  backdrop-filter:blur(20px) saturate(1.4)!important;
  -webkit-backdrop-filter:blur(20px) saturate(1.4)!important;
  border-right:1px solid var(--border)!important;
  z-index:10;
}}
[data-testid="stSidebar"] *{{color:var(--text)!important}}
[data-testid="stSidebar"] label{{
  color:var(--lc)!important;font-size:0.72rem!important;font-weight:700!important;
  letter-spacing:.12em!important;text-transform:uppercase!important
}}
[data-testid="stSidebar"] input{{
  background:var(--glass2)!important;color:var(--text)!important;
  border:1px solid var(--border2)!important;border-radius:10px!important;
  font-size:0.95rem!important;
  backdrop-filter:blur(8px)!important;
}}

/* ── GLASSMORPHISM INPUTS ── */
textarea,input[type="text"],input[type="number"],.stNumberInput input{{
  background:var(--glass)!important;
  color:var(--text)!important;
  border:1.5px solid var(--border2)!important;
  border-radius:12px!important;
  font-family:'Outfit','Inter',sans-serif!important;
  font-size:1rem!important;
  line-height:1.65!important;
  caret-color:var(--a1)!important;
  padding:12px 16px!important;
  backdrop-filter:blur(8px)!important;
  transition:all 0.25s ease!important;
}}
textarea:focus,input:focus{{
  border-color:var(--a1)!important;
  box-shadow:0 0 0 4px color-mix(in srgb,var(--a1) 15%,transparent), var(--neon_teal)!important;
  transform:translateY(-1px)!important;
}}
textarea::placeholder,input::placeholder{{color:var(--text3)!important;font-size:0.92rem!important}}
.stTextArea label,.stTextInput label,.stNumberInput label{{
  color:var(--lc)!important;font-size:0.72rem!important;
  font-weight:700!important;letter-spacing:.12em!important;text-transform:uppercase!important
}}

/* ── TABS WITH GLASS EFFECT ── */
[data-testid="stTabs"] [role="tablist"]{{
  background:var(--glass)!important;
  backdrop-filter:blur(16px)!important;
  border-bottom:1px solid var(--border)!important;
  padding:0 12px;gap:6px;
  border-radius:14px 14px 0 0!important;
  margin-bottom:2px!important;
}}
[data-testid="stTabs"] button[role="tab"]{{
  color:var(--text2)!important;font-family:'Outfit',sans-serif!important;
  font-weight:700!important;font-size:0.9rem!important;
  letter-spacing:.02em!important;border:none!important;
  background:transparent!important;padding:14px 22px!important;border-radius:0!important;
  position:relative!important;overflow:hidden!important;
  transition:color 0.3s!important;
}}
[data-testid="stTabs"] button[role="tab"]::after{{
  content:'';position:absolute;bottom:0;left:50%;right:50%;height:2.5px;
  background:var(--a1);border-radius:2px;transition:all 0.35s cubic-bezier(0.4,0,0.2,1);
}}
[data-testid="stTabs"] button[role="tab"]:hover::after{{
  left:25%!important;right:25%!important;
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{{
  color:var(--a1)!important;
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]::after{{
  left:10%!important;right:10%!important;
}}

/* ── BUTTONS WITH NEON GLOW ── */
.stButton>button{{
  background:var(--glass)!important;color:var(--text)!important;
  border:1.5px solid var(--border2)!important;border-radius:12px!important;
  font-family:'Outfit',sans-serif!important;font-weight:700!important;
  font-size:0.92rem!important;transition:all .25s ease!important;padding:9px 18px!important;
  backdrop-filter:blur(8px)!important;
}}
.stButton>button:hover{{
  background:var(--bg2)!important;border-color:var(--a1)!important;color:var(--a1)!important;
  box-shadow:var(--neon_teal)!important;transform:translateY(-2px)!important;
}}
.stDownloadButton>button{{
  background:linear-gradient(135deg,var(--a1),color-mix(in srgb,var(--a1) 60%,black))!important;
  color:#000!important;border:none!important;font-weight:800!important;font-size:0.9rem!important;
  border-radius:12px!important;transition:all .25s ease!important;
  box-shadow:var(--neon_teal)!important;
}}
.stDownloadButton>button:hover{{
  transform:translateY(-2px)!important;
  box-shadow:0 8px 24px rgba(0,212,170,0.35)!important;
}}

/* ── ALERTS GLASS ── */
[data-testid="stAlert"]{{
  background:var(--glass)!important;
  backdrop-filter:blur(12px)!important;
  border-color:var(--border)!important;color:var(--text)!important;
  border-radius:12px!important;
}}

/* ── FILE UPLOADER GLASS ── */
[data-testid="stFileUploadDropzone"]{{
  background:var(--glass2)!important;
  backdrop-filter:blur(8px)!important;
  border:2px dashed var(--border2)!important;
  border-radius:12px!important;color:var(--text2)!important;
  transition:all 0.3s!important;
}}
[data-testid="stFileUploadDropzone"]:hover{{
  border-color:var(--a1)!important;
  background:color-mix(in srgb,var(--a1) 5%,var(--glass2))!important;
}}

/* ── PROGRESS BAR ANIMATED ── */
.stProgress>div>div>div{{
  background:linear-gradient(90deg,var(--a1),var(--green))!important;
  background-size:200% 100%!important;
  animation:gradientFlow 2s ease infinite!important;
}}
@keyframes gradientFlow {{
  0%{{background-position:0% 50%;}}
  50%{{background-position:100% 50%;}}
  100%{{background-position:0% 50%;}}
}}
.stProgress>div>div{{background:var(--bg3)!important;border-radius:6px!important}}

/* ── GLASS CANVAS CARD ── */
.ccard{{
  background:var(--glass)!important;
  backdrop-filter:blur(16px) saturate(1.3)!important;
  -webkit-backdrop-filter:blur(16px) saturate(1.3)!important;
  border:1px solid var(--border);
  border-radius:14px;padding:16px 18px;margin-bottom:12px;
  transition:all 0.35s cubic-bezier(0.4,0,0.2,1);
  position:relative;overflow:hidden;
}}
.ccard::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:4px;
  background:linear-gradient(90deg,transparent,var(--a1),transparent);
  opacity:0.6;
}}
.ccard:hover{{
  border-color:var(--border2);
  box-shadow:var(--shadow),var(--neon_teal);
  transform:translateY(-4px);
}}
.ccard-title{{font-size:0.75rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px}}

/* ── GLASS HERO WITH MESH GRADIENT ── */
.hero{{
  background:linear-gradient({T['hero_grad']});
  border:1px solid var(--border);border-radius:20px;
  padding:30px 36px;margin-bottom:22px;box-shadow:var(--shadow);
  display:flex;align-items:center;justify-content:space-between;
  position:relative;overflow:hidden;
  backdrop-filter:blur(16px)!important;
}}
.hero::before{{
  content:'';position:absolute;top:-50%;right:-20%;width:500px;height:500px;
  background:radial-gradient(circle,{T['mesh1']},transparent);
  animation:heroGlow 8s ease-in-out infinite alternate;
  pointer-events:none;
}}
.hero::after{{
  content:'';position:absolute;bottom:-30%;left:-10%;width:400px;height:400px;
  background:radial-gradient(circle,{T['mesh2']},transparent);
  animation:heroGlow 10s ease-in-out infinite alternate-reverse;
  pointer-events:none;
}}
@keyframes heroGlow {{
  0%{{transform:translate(0,0) scale(1);opacity:0.6;}}
  100%{{transform:translate(40px,-30px) scale(1.1);opacity:1;}}
}}

/* ── GLASS METRIC BOX ── */
.mbox{{
  background:var(--glass)!important;
  backdrop-filter:blur(16px)!important;
  border:1px solid var(--border);
  border-radius:14px;padding:20px 24px;text-align:center;
  transition:all 0.35s cubic-bezier(0.4,0,0.2,1);
  position:relative;overflow:hidden;
}}
.mbox::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--a1),var(--a3));
  opacity:0.5;
}}
.mbox:hover{{
  box-shadow:var(--shadow),var(--neon_indigo);
  transform:translateY(-4px) scale(1.02);
  border-color:var(--border2);
}}
.mval{{font-size:2.2rem;font-weight:900;margin:0;line-height:1;letter-spacing:-0.03em}}
.mlbl{{font-size:0.72rem;color:var(--text2);text-transform:uppercase;letter-spacing:.14em;margin-top:6px;font-weight:600}}

/* ── SUMMARY CARD ── */
.scard{{
  background:var(--glass)!important;
  backdrop-filter:blur(12px)!important;
  border:1px solid var(--border);
  border-radius:12px;padding:14px 18px;margin-bottom:10px;min-height:70px;
  position:relative;overflow:hidden;
  transition:all 0.25s ease;
}}
.scard:hover{{border-color:var(--border2);box-shadow:var(--shadow_sm);}}
.scard-lbl{{font-size:0.68rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}}
.scard-val{{font-size:0.95rem;color:var(--text);white-space:pre-wrap;line-height:1.6}}
.scard-empty{{font-size:0.9rem;color:var(--text3);font-style:italic}}

/* ── FILE CHIP GLASS ── */
.fchip{{
  background:var(--glass2)!important;
  backdrop-filter:blur(8px)!important;
  border:1px solid var(--border);
  border-left:3px solid var(--a1);border-radius:10px;
  padding:9px 14px;margin-bottom:7px;font-size:0.9rem;font-weight:600;
  transition:all 0.2s ease;
}}
.fchip:hover{{border-color:var(--a1);box-shadow:var(--neon_teal);}}
.fchip.act{{border-left-color:var(--a2);}}

/* ── TIP BOX GLASS ── */
.tipbox{{
  background:{T['tip_bg']}!important;
  backdrop-filter:blur(12px)!important;
  border:1px solid {T['tip_border']};
  border-left:3px solid var(--a1);
  border-radius:12px;padding:14px 20px;font-size:0.94rem;color:var(--text2);margin-bottom:18px;
}}

/* ── INFO BANNER GLASS ── */
.ibanner{{
  background:{T['ibanner_bg']}!important;
  backdrop-filter:blur(12px)!important;
  border:1px solid {T['ibanner_border']};
  border-left:3px solid var(--a3);border-radius:12px;
  padding:14px 20px;font-size:0.94rem;color:var(--text2);margin-bottom:18px;
}}

/* ── CHECKLIST ITEM ── */
.chk{{
  padding:12px 18px;background:var(--glass2)!important;
  backdrop-filter:blur(8px)!important;
  border-radius:10px;
  border:1px solid transparent;
  margin-bottom:8px;font-size:0.95rem;transition:all 0.25s ease;
}}
.chk:hover{{border-color:var(--border2);transform:translateX(4px);}}

/* ── POWER PROMPT ── */
.ppbox{{
  background:var(--glass2)!important;
  backdrop-filter:blur(8px)!important;
  border:1px solid var(--border);
  border-left:3px solid var(--a2);border-radius:12px;
  padding:14px 18px;margin-bottom:10px;
  transition:all 0.25s ease;
}}
.ppbox:hover{{box-shadow:var(--neon_orange)!important;transform:translateY(-2px);}}
.pptitle{{font-size:0.72rem;font-weight:800;color:var(--a2);letter-spacing:.13em;text-transform:uppercase}}
.pptext{{font-size:0.94rem;color:var(--text2);margin-top:6px;line-height:1.6}}

/* ── RADAR BARS ENHANCED ── */
.radar-wrap{{display:flex;flex-direction:column;gap:10px;padding:4px 0}}
.rbar-row{{display:flex;align-items:center;gap:12px}}
.rbar-lbl{{font-size:0.8rem;color:var(--text2);width:160px;text-align:right;flex-shrink:0;font-weight:600}}
.rbar-track{{flex:1;height:12px;background:var(--bg3);border-radius:6px;overflow:hidden}}
.rbar-fill{{height:12px;border-radius:6px;transition:width 0.8s cubic-bezier(0.4,0,0.2,1);
  background:linear-gradient(90deg,var(--a1),var(--green))!important;
  background-size:200% 100%!important;
  animation:gradientFlow 3s ease infinite!important;
}}
.rbar-pct{{font-size:0.78rem;font-family:'JetBrains Mono',monospace;color:var(--text3);width:40px}}

/* ── VPC FIT CARD GLASS ── */
.fitcard{{
  background:var(--glass2)!important;
  backdrop-filter:blur(8px)!important;
  border:1px solid var(--border);border-radius:12px;
  padding:16px 20px;margin-bottom:12px;
  transition:all 0.25s ease;
}}
.fitcard:hover{{border-color:var(--a2);box-shadow:var(--shadow_sm);transform:translateY(-2px);}}
.fitcard-arrow{{font-size:0.78rem;font-weight:800;color:var(--text2);letter-spacing:.11em;text-transform:uppercase;margin-bottom:6px}}
.fitcard-status{{font-size:1rem;font-weight:700}}

/* ── SECTION DIVIDER ── */
.sdiv{{border:none;border-top:1px solid var(--border);margin:24px 0}}

/* ── GLASS CHART CARD ── */
.chart-card{{
  background:var(--glass)!important;
  backdrop-filter:blur(16px)!important;
  border:1px solid var(--border);
  border-radius:16px;
  padding:20px;
  margin-bottom:16px;
  transition:all 0.35s cubic-bezier(0.4,0,0.2,1);
}}
.chart-card:hover{{
  border-color:var(--border2);
  box-shadow:var(--shadow);
  transform:translateY(-3px);
}}
.chart-card::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  border-radius:16px 16px 0 0;
  background:linear-gradient(90deg,var(--a1),var(--a3),var(--a5));
  opacity:0.4;
}}

/* ── ANIMATED PROGRESS RING ── */
@keyframes ringPulse {{
  0%{{filter:drop-shadow(0 0 4px var(--glow_teal));}}
  50%{{filter:drop-shadow(0 0 12px var(--glow_teal));}}
  100%{{filter:drop-shadow(0 0 4px var(--glow_teal));}}
}}
.ring-wrap{{animation:ringPulse 3s ease-in-out infinite;}}

/* ── FLOATING BADGE ── */
@keyframes float {{
  0%,100%{{transform:translateY(0px);}}
  50%{{transform:translateY(-6px);}}
}}
.float-badge{{animation:float 3s ease-in-out infinite;}}

/* ── SHIMMER EFFECT ── */
@keyframes shimmer {{
  0%{{background-position:-200% 0;}}
  100%{{background-position:200% 0;}}
}}
.shimmer{{
  background:linear-gradient(90deg,transparent 0%,{T['text2']}20 50%,transparent 100%);
  background-size:200% 100%;
  animation:shimmer 2.5s infinite;
}}

/* ── STAGGERED FADE IN ── */
@keyframes fadeInUp {{
  from{{opacity:0;transform:translateY(20px);}}
  to{{opacity:1;transform:translateY(0);}}
}}
.fade-in{{animation:fadeInUp 0.6s ease forwards;}}

/* ── GLASS STAT ROW ── */
.stat-row{{
  display:flex;
  align-items:center;
  gap:12px;
  padding:14px 16px;
  background:var(--glass2)!important;
  backdrop-filter:blur(8px)!important;
  border:1px solid var(--border);
  border-radius:12px;
  margin-bottom:8px;
  transition:all 0.25s ease;
}}
.stat-row:hover{{border-color:var(--a1);box-shadow:var(--neon_teal);transform:translateX(4px);}}

/* ── TIMELINE ITEM ── */
.timeline-item{{
  position:relative;
  padding-left:30px;
  padding-bottom:20px;
  border-left:2px solid var(--border);
  margin-left:10px;
}}
.timeline-item::before{{
  content:'';
  position:absolute;
  left:-6px;
  top:4px;
  width:10px;
  height:10px;
  border-radius:50%;
  background:var(--a1);
  box-shadow:0 0 8px var(--glow_teal);
}}
.timeline-item.active::before{{
  background:var(--a2);
  box-shadow:var(--neon_orange);
}}
.timeline-item.done::before{{
  background:var(--green);
}}
/* --- RESPONSIVE MOBILE TWEAKS --- */
@media (max-width: 768px) {
  .hero {
    flex-direction: column !important;
    text-align: center !important;
    padding: 20px !important;
    gap: 20px !important;
  }
  .hero > div {
    text-align: center !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
  }
  .hero div[style*="justify-content:flex-end"] {
    justify-content: center !important;
  }
  .mbox {
    padding: 15px !important;
  }
  .mval {
    font-size: 1.8rem !important;
  }
}
</style>
""", unsafe_allow_html=True)


# ── FIELD DEFS ────────────────────────────────────────────────
BMC = ["key_partners","key_activities","value_propositions",
       "customer_relationships","customer_segments","key_resources",
       "channels","cost_structure","revenue_streams"]
VPC = ["customer_jobs","customer_pains","customer_gains",
       "products_services","pain_relievers","gain_creators"]
SWOT = ["swot_s","swot_w","swot_o","swot_t"]
ALL = BMC + VPC + SWOT

LABELS = {
    "key_partners":"🤝 Key Partners","key_activities":"⚙️ Key Activities",
    "value_propositions":"💎 Value Propositions",
    "customer_relationships":"💬 Customer Relationships",
    "customer_segments":"👥 Customer Segments","key_resources":"🧱 Key Resources",
    "channels":"📣 Channels","cost_structure":"💸 Cost Structure",
    "revenue_streams":"💰 Revenue Streams","customer_jobs":"🧑‍💼 Customer Jobs",
    "customer_pains":"😣 Pains","customer_gains":"😊 Gains",
    "products_services":"🛠️ Products & Services","pain_relievers":"🩹 Pain Relievers",
    "gain_creators":"🎁 Gain Creators",
    "swot_s":"💪 Strengths","swot_w":"⚠️ Weaknesses",
    "swot_o":"🚀 Opportunities","swot_t":"🔥 Threats",
}
PLAIN = {k: v.split(" ", 1)[1] for k, v in LABELS.items()}
COLORS = {
    "key_partners":"amber","key_activities":"amber","value_propositions":"indigo",
    "customer_relationships":"teal","customer_segments":"teal","key_resources":"orange",
    "channels":"teal","cost_structure":"red","revenue_streams":"green",
    "customer_jobs":"indigo","customer_pains":"red","customer_gains":"green",
    "products_services":"teal","pain_relievers":"red","gain_creators":"green",
    "swot_s":"green","swot_w":"red","swot_o":"indigo","swot_t":"orange",
}
ACCENT_MAP = {"teal":"var(--a1)","orange":"var(--a2)","indigo":"var(--a3)",
              "amber":"var(--a4)","red":"var(--red)","green":"var(--green)"}
HEX_MAP = {"teal":"#00d4aa","orange":"#ff6b35","indigo":"#6c7fff",
           "amber":"#f7c948","red":"#e05252","green":"#3ecf8e"}

# Dark-mode Plotly colors
PLOTLY_DARK = {"bg":"#13131f","card":"#1a1a2e","text":"#f0f0fa","text2":"#a0a0c8","grid":"#2a2a45"}
PLOTLY_LIGHT = {"bg":"#ffffff","card":"#f5f7ff","text":"#12122a","text2":"#3d3d6a","grid":"#e8ecf8"}

HINTS = {
    "key_partners":      "Who are your key suppliers and strategic partners?",
    "key_activities":    "What critical activities must your business perform?",
    "value_propositions":"What value do you deliver? What problem do you solve?",
    "customer_relationships":"How do you interact with each customer segment?",
    "customer_segments": "Who are your most important customers?",
    "key_resources":     "Physical, intellectual, human, or financial resources?",
    "channels":          "How do you reach and serve your customer segments?",
    "cost_structure":    "What are your most significant cost drivers?",
    "revenue_streams":   "How do customers pay? What are they willing to pay for?",
    "customer_jobs":     "What functional, social, or emotional tasks are they doing?",
    "customer_pains":    "What frustrates, annoys, or risks affecting your customer?",
    "customer_gains":    "What outcomes and benefits do they desire?",
    "products_services": "List your core products and services.",
    "pain_relievers":    "How does your offer eliminate specific customer pains?",
    "gain_creators":     "How does your offer create the gains customers want?",
    "swot_s": "What are your internal advantages?",
    "swot_w": "What internal areas need improvement?",
    "swot_o": "What external factors can you exploit?",
    "swot_t": "What external factors could cause trouble?",
}

# ── HELPERS ───────────────────────────────────────────────────
def snapshot():
    st.session_state.history.append(dict(st.session_state.canvas))
    if len(st.session_state.history) > 30: st.session_state.history.pop(0)

def undo():
    if st.session_state.history:
        st.session_state.canvas = st.session_state.history.pop()

def save_canvas(name):
    snapshot()
    st.session_state.saved_files[name] = dict(st.session_state.canvas)
    st.session_state.active_file = name
    st.session_state.last_saved = datetime.now().strftime("%H:%M")

def load_canvas(name):
    snapshot()
    st.session_state.canvas = dict(st.session_state.saved_files[name])
    st.session_state.file_name = name
    st.session_state.active_file = name

def delete_canvas(name):
    st.session_state.saved_files.pop(name, None)
    if st.session_state.active_file == name:
        st.session_state.active_file = None

def clear_canvas():
    snapshot()
    st.session_state.canvas = {f: "" for f in ALL}

def to_json(name):
    return json.dumps({
        "file_name": name,
        "founder_name": st.session_state.get("founder_name", ""),
        "company_name": st.session_state.get("company_name", ""),
        "canvas": st.session_state.canvas,
        "exported_at": datetime.now().isoformat(),
        "version": "5.0"
    }, indent=2)

def to_csv(name):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Section", "Field", "Content"])
    for f in BMC: w.writerow(["BMC", PLAIN[f], st.session_state.canvas[f]])
    for f in VPC: w.writerow(["VPC", PLAIN[f], st.session_state.canvas[f]])
    for f in SWOT: w.writerow(["SWOT", PLAIN[f], st.session_state.canvas[f]])
    return buf.getvalue()

# ── PDF EXPORT WITH FOUNDER NAME & CANVAS NAME ────────────────
def to_pdf(name, size="A4", orientation="Landscape"):
    try:
        from reportlab.lib.pagesizes import A4, A5, A3, letter, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas as C
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        founder = st.session_state.get("founder_name", "") or "Unknown Author"
        company = st.session_state.get("company_name", "") or ""

        sizes = {"A3": A3, "A4": A4, "A5": A5, "Letter": letter}
        psize = sizes.get(size, A4)
        if orientation == "Landscape":
            pw, ph = landscape(psize)
        else:
            pw, ph = psize
        buf = io.BytesIO()
        c = C.Canvas(buf, pagesize=(pw, ph))

        # Colors
        WHITE  = colors.white
        DARK   = colors.HexColor("#13131f")
        TEAL   = colors.HexColor("#00d4aa")
        ORANGE = colors.HexColor("#ff6b35")
        INDIGO = colors.HexColor("#6c7fff")
        AMBER  = colors.HexColor("#f7c948")
        REDC   = colors.HexColor("#e05252")
        GREENC = colors.HexColor("#3ecf8e")
        LIGHTBG= colors.HexColor("#1a1a2e")
        MID    = colors.HexColor("#2a2a45")

        SEC_COL = {
            "key_partners": AMBER, "key_activities": AMBER, "value_propositions": INDIGO,
            "customer_relationships": TEAL, "customer_segments": TEAL, "key_resources": ORANGE,
            "channels": TEAL, "cost_structure": REDC, "revenue_streams": GREENC,
            "customer_jobs": INDIGO, "customer_pains": REDC, "customer_gains": GREENC,
            "products_services": TEAL, "pain_relievers": REDC, "gain_creators": GREENC,
            "swot_s": GREENC, "swot_w": REDC, "swot_o": INDIGO, "swot_t": ORANGE,
        }

        def draw_cell(x, y, cw, ch, key, content):
            col = SEC_COL.get(key, TEAL)
            # Subtle Shadow
            c.setFillColor(colors.HexColor("#2a2a45"))
            c.roundRect(x+0.8, y-0.8, cw, ch, 4, fill=1, stroke=0)
            
            # Cell Background
            c.setFillColor(LIGHTBG)
            c.roundRect(x, y, cw, ch, 4, fill=1, stroke=0)
            
            # Header Bar (Increased height for larger font)
            hh = 10 # Header height
            c.setFillColor(col)
            c.roundRect(x, y+ch-hh, cw, hh, 3, fill=1, stroke=0)
            c.rect(x, y+ch-hh+3, cw, hh-3, fill=1, stroke=0) # Flatten bottom of header roundrect
            
            # Header Text (Increased to 9)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 9)
            # Center title slightly or keep it left-aligned
            c.drawString(x+4, y+ch-hh+2.5, PLAIN.get(key, "").upper())
            
            # Content Text (Increased to 9)
            c.setFillColor(colors.HexColor("#f0f0fa"))
            c.setFont("Helvetica", 9)
            lines = (content or "—").split("\n")
            ty = y+ch-hh-6
            line_height = 11
            # Safer character count estimation (ReportLab units are points, 1pt ~ 0.35mm)
            # cw is in points. Helvetica 9pt average char width is ~5pt.
            chars_per_line = max(10, int(cw / 4.8)) 
            
            for line in lines:
                if ty < y+5: break
                # Simple word wrap logic
                words = line.split(' ')
                curr_line = ""
                for w in words:
                    if len(curr_line + w) < chars_per_line:
                        curr_line += w + " "
                    else:
                        c.drawString(x+5, ty, curr_line.strip())
                        ty -= line_height
                        curr_line = w + " "
                        if ty < y+5: break
                if ty >= y+5 and curr_line:
                    c.drawString(x+5, ty, curr_line.strip())
                    ty -= line_height

        # ===== PAGE 1: COVER / HEADER =====
        c.setFillColor(DARK); c.rect(0, 0, pw, ph, fill=1, stroke=0)

        # Header bar
        c.setFillColor(TEAL)
        c.rect(0, ph-18*mm, pw, 18*mm, fill=1, stroke=0)

        # Canvas name
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 16)
        display_name = name.replace("_", " ").title()
        c.drawString(10*mm, ph-11*mm, display_name)

        # Founder & Company
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#a0a0c8"))
        meta_text = f"by {founder}"
        if company:
            meta_text += f"  ·  {company}"
        c.drawRightString(pw-10*mm, ph-11*mm, meta_text)

        # Date
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#55557a"))
        c.drawRightString(pw-10*mm, ph-15*mm, f"{size} · {orientation} · {datetime.now().strftime('%d %b %Y')}")

        # Decorative accent line
        c.setStrokeColor(TEAL)
        c.setLineWidth(1)
        c.line(10*mm, ph-22*mm, pw-10*mm, ph-22*mm)

        # Subtitle
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#00d4aa"))
        c.drawString(10*mm, ph-29*mm, "BUSINESS MODEL CANVAS")

        pad = 12*mm; top = ph-32*mm; bot = 18*mm
        uw = pw-2*pad; uh = top-bot
        cw = [uw*.2]*5
        x0,x1,x2,x3,x4 = [pad+sum(cw[:i]) for i in range(5)]

        if orientation == "Landscape":
            rh = uh*.66; r2h = uh-rh
            yr1 = bot+r2h
            # Column 1
            draw_cell(x0, yr1, cw[0]-2, rh-2, "key_partners", st.session_state.canvas["key_partners"])
            # Column 2
            draw_cell(x1, yr1+rh*.5, cw[1]-2, rh*.5-2, "key_activities", st.session_state.canvas["key_activities"])
            draw_cell(x1, yr1, cw[1]-2, rh*.5-2, "key_resources", st.session_state.canvas["key_resources"])
            # Column 3
            draw_cell(x2, yr1, cw[2]-2, rh-2, "value_propositions", st.session_state.canvas["value_propositions"])
            # Column 4
            draw_cell(x3, yr1+rh*.5, cw[3]-2, rh*.5-2, "customer_relationships", st.session_state.canvas["customer_relationships"])
            draw_cell(x3, yr1, cw[3]-2, rh*.5-2, "channels", st.session_state.canvas["channels"])
            # Column 5
            draw_cell(x4, yr1, cw[4]-2, rh-2, "customer_segments", st.session_state.canvas["customer_segments"])
            # Bottom row
            draw_cell(pad, bot, uw/2-2, r2h-2, "cost_structure", st.session_state.canvas["cost_structure"])
            draw_cell(pad+uw/2+2, bot, uw/2-2, r2h-2, "revenue_streams", st.session_state.canvas["revenue_streams"])
        else:
            # Portrait: 3x3 Grid for BMC
            ph_uh = uh / 3.2
            cw3 = uw / 3
            
            # Row 1
            draw_cell(x0, top-ph_uh, cw3-2, ph_uh-4, "key_partners", st.session_state.canvas["key_partners"])
            draw_cell(x0+cw3, top-ph_uh, cw3-2, ph_uh-4, "key_activities", st.session_state.canvas["key_activities"])
            draw_cell(x0+cw3*2, top-ph_uh, cw3-2, ph_uh-4, "value_propositions", st.session_state.canvas["value_propositions"])
            
            # Row 2
            draw_cell(x0, top-ph_uh*2.1, cw3-2, ph_uh*1.1-4, "key_resources", st.session_state.canvas["key_resources"])
            draw_cell(x0+cw3, top-ph_uh*2.1, cw3-2, ph_uh*1.1-4, "customer_relationships", st.session_state.canvas["customer_relationships"])
            draw_cell(x0+cw3*2, top-ph_uh*2.1, cw3-2, ph_uh*1.1-4, "customer_segments", st.session_state.canvas["customer_segments"])
            
            # Row 3 (Bottom)
            bh = uh - (ph_uh * 2.1)
            draw_cell(x0, bot, cw3-2, bh-2, "channels", st.session_state.canvas["channels"])
            draw_cell(x0+cw3, bot, cw3-2, bh-2, "cost_structure", st.session_state.canvas["cost_structure"])
            draw_cell(x0+cw3*2, bot, cw3-2, bh-2, "revenue_streams", st.session_state.canvas["revenue_streams"])

        # Footer
        c.setFillColor(colors.HexColor("#0d1520")); c.rect(0, 0, pw, 6*mm, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#55557a")); c.setFont("Helvetica", 6)
        c.drawCentredString(pw/2, 2.5*mm, f"Canvas Studio Pro  ·  Strategy Toolkit  ·  {display_name}")
        c.showPage()

        # ===== PAGE 2: VPC TEXT BLOCKS =====
        c.setFillColor(DARK); c.rect(0, 0, pw, ph, fill=1, stroke=0)
        c.setFillColor(ORANGE); c.rect(0, ph-18*mm, pw, 18*mm, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 16)
        c.drawString(10*mm, ph-11*mm, display_name)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#a0a0c8"))
        meta_text2 = f"by {founder}"
        if company: meta_text2 += f"  ·  {company}"
        c.drawRightString(pw-10*mm, ph-11*mm, meta_text2)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#55557a"))
        c.drawRightString(pw-10*mm, ph-15*mm, f"{size} · {orientation} · {datetime.now().strftime('%d %b %Y')}")

        c.setStrokeColor(ORANGE); c.setLineWidth(1)
        c.line(10*mm, ph-22*mm, pw-10*mm, ph-22*mm)
        c.setFont("Helvetica-Bold", 14); c.setFillColor(ORANGE)
        c.drawString(10*mm, ph-29*mm, "VALUE PROPOSITION — DETAILS")

        v_top = ph-34*mm; v_bot = 12*mm; v_uh = v_top-v_bot
        ch_v = v_uh/3 - 4*mm
        v_lw = uw/2 - 4*mm
        
        # Left side: Value Map
        for i, fk in enumerate(["products_services","gain_creators","pain_relievers"]):
            fy = v_top - (i+1)*(ch_v+4*mm)
            draw_cell(pad, fy, v_lw, ch_v, fk, st.session_state.canvas[fk])
        # Right side: Customer Profile
        for i, fk in enumerate(["customer_jobs","customer_gains","customer_pains"]):
            fy = v_top - (i+1)*(ch_v+4*mm)
            draw_cell(pad+uw/2+4*mm, fy, v_lw, ch_v, fk, st.session_state.canvas[fk])
            
        c.showPage()

        # ===== PAGE 3: VPC VISUAL DIAGRAMS =====
        c.setFillColor(DARK); c.rect(0, 0, pw, ph, fill=1, stroke=0)
        c.setFillColor(ORANGE); c.rect(0, ph-18*mm, pw, 18*mm, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 16)
        c.drawString(10*mm, ph-11*mm, display_name)
        c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#55557a"))
        c.drawRightString(pw-10*mm, ph-15*mm, "Value Proposition Fit Analysis")

        c.setStrokeColor(ORANGE); c.setLineWidth(1)
        c.line(10*mm, ph-22*mm, pw-10*mm, ph-22*mm)
        c.setFont("Helvetica-Bold", 14); c.setFillColor(ORANGE)
        c.drawString(10*mm, ph-29*mm, "VALUE PROPOSITION CANVAS — VISUAL FIT")

        # Helper for small text inside diagrams
        def draw_diag_text(tx, ty, tw, content, color):
            c.setFillColor(color)
            c.setFont("Helvetica", 7.5)
            dlines = (content or "").split("\n")[:3] # Max 3 lines
            for i, dline in enumerate(dlines):
                if len(dline) > int(tw/2.5): dline = dline[:int(tw/2.5)-3] + "..."
                c.drawCentredString(tx, ty - i*9, dline)

        mx = pw/2; my = ph/2 - 10*mm
        rad = min(pw, ph) * (0.26 if orientation=="Landscape" else 0.18)
        
        # --- VALUE MAP (Square) ---
        sx = mx - rad*2 - 15*mm if orientation=="Landscape" else mx - rad
        sy = my - rad if orientation=="Landscape" else my + rad + 8*mm
        c.setStrokeColor(ORANGE); c.setLineWidth(2); c.setFillColor(colors.HexColor("#1f1410"))
        c.roundRect(sx, sy, rad*2, rad*2, 8, fill=1, stroke=1)
        # Standard VPC Divisions
        c.setLineWidth(1); c.setStrokeColor(colors.HexColor("#4a2a1a"))
        c.line(sx+rad*0.8, sy, sx+rad*0.8, sy+rad*2) # Vertical split for Products
        c.line(sx+rad*0.8, sy+rad, sx+rad*2, sy+rad) # Horizontal split for Gains/Pains
        
        c.setFont("Helvetica-Bold", 12); c.setFillColor(ORANGE)
        c.drawCentredString(sx+rad, sy+rad*2+5*mm, "VALUE MAP")
        
        # Words inside Square
        c.setFont("Helvetica-Bold", 7); c.setFillColor(ORANGE)
        c.drawCentredString(sx+rad*0.4, sy+rad+18, "PRODUCTS")
        draw_diag_text(sx+rad*0.4, sy+rad+5, rad*0.7, st.session_state.canvas["products_services"], WHITE)
        
        c.drawCentredString(sx+rad*1.4, sy+rad*1.5+8, "GAIN CREATORS")
        draw_diag_text(sx+rad*1.4, sy+rad*1.5-5, rad*1.1, st.session_state.canvas["gain_creators"], WHITE)
        
        c.drawCentredString(sx+rad*1.4, sy+rad*0.5+8, "PAIN RELIEVERS")
        draw_diag_text(sx+rad*1.4, sy+rad*0.5-5, rad*1.1, st.session_state.canvas["pain_relievers"], WHITE)

        # --- CUSTOMER PROFILE (Circle) ---
        cx = mx + 15*mm + rad if orientation=="Landscape" else mx
        cy = my if orientation=="Landscape" else my - rad*2 - 15*mm
        c.setStrokeColor(TEAL); c.setLineWidth(2); c.setFillColor(colors.HexColor("#101f1d"))
        c.circle(cx, cy, rad, fill=1, stroke=1)
        # Standard VPC Divisions
        c.setLineWidth(1); c.setStrokeColor(colors.HexColor("#1a4a45"))
        c.line(cx+rad*0.2, cy-rad*0.98, cx+rad*0.2, cy+rad*0.98) # Vertical split
        c.line(cx-rad*0.98, cy, cx+rad*0.2, cy) # Horizontal split for Gains/Pains
        
        c.setFont("Helvetica-Bold", 12); c.setFillColor(TEAL)
        c.drawCentredString(cx, cy+rad+5*mm, "CUSTOMER PROFILE")
        
        # Words inside Circle
        c.setFont("Helvetica-Bold", 7); c.setFillColor(TEAL)
        c.drawCentredString(cx+rad*0.6, cy+18, "JOBS")
        draw_diag_text(cx+rad*0.6, cy+5, rad*0.7, st.session_state.canvas["customer_jobs"], WHITE)
        
        c.drawCentredString(cx-rad*0.4, cy+rad*0.5+8, "GAINS")
        draw_diag_text(cx-rad*0.4, cy+rad*0.5-5, rad*0.7, st.session_state.canvas["customer_gains"], WHITE)
        
        c.drawCentredString(cx-rad*0.4, cy-rad*0.5+8, "PAINS")
        draw_diag_text(cx-rad*0.4, cy-rad*0.5-5, rad*0.7, st.session_state.canvas["customer_pains"], WHITE)
        
        # Connection Arrow
        c.setStrokeColor(colors.HexColor("#55557a")); c.setLineWidth(3)
        if orientation=="Landscape":
            c.line(mx-10*mm, my, mx+10*mm, my)
        else:
            # Vertical arrow between Square (top) and Circle (bot)
            ay = (sy + cy + rad) / 2
            c.line(mx, ay-6*mm, mx, ay+6*mm)

        c.showPage()

        # ===== PAGE 4: SWOT ANALYSIS =====
        c.setFillColor(DARK); c.rect(0, 0, pw, ph, fill=1, stroke=0)
        c.setFillColor(INDIGO); c.rect(0, ph-18*mm, pw, 18*mm, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 16)
        c.drawString(10*mm, ph-11*mm, display_name)
        c.setFont("Helvetica-Bold", 14); c.setFillColor(INDIGO)
        c.drawString(10*mm, ph-29*mm, "SWOT ANALYSIS")

        sq = min(pw, ph) * 0.40
        ox = (pw - sq*2) / 2
        oy = (ph - sq*2) / 2 - 10*mm
        draw_cell(ox, oy+sq, sq-2, sq-2, "swot_s", st.session_state.canvas["swot_s"])
        draw_cell(ox+sq, oy+sq, sq-2, sq-2, "swot_w", st.session_state.canvas["swot_w"])
        draw_cell(ox, oy, sq-2, sq-2, "swot_o", st.session_state.canvas["swot_o"])
        draw_cell(ox+sq, oy, sq-2, sq-2, "swot_t", st.session_state.canvas["swot_t"])

        # Footer
        c.setFillColor(colors.HexColor("#0d1520")); c.rect(0, 0, pw, 6*mm, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#55557a")); c.setFont("Helvetica", 6)
        c.drawCentredString(pw/2, 2.5*mm, f"Canvas Studio Pro  ·  Strategy Toolkit  ·  {display_name}")
        c.showPage(); c.save()
        return buf.getvalue()
    except ImportError:
        return None

# ── LOAD/UPLOAD ──────────────────────────────────────────────
def load_upload(f):
    try:
        data = f.read()
        if f.name.endswith(".json"):
            d = json.loads(data)
            snapshot()
            st.session_state.canvas = {k: d.get("canvas", {}).get(k, "") for k in ALL}
            st.session_state.founder_name = d.get("founder_name", "")
            st.session_state.company_name = d.get("company_name", "")
            n = d.get("file_name", f.name.replace(".json", ""))
            st.session_state.file_name = n
            st.session_state.saved_files[n] = dict(st.session_state.canvas)
            st.session_state.active_file = n
            return True, f"Loaded **{n}**"
        elif f.name.endswith(".csv"):
            lmap = {v: k for k, v in PLAIN.items()}
            nc = {k: "" for k in ALL}
            for row in csv.DictReader(io.StringIO(data.decode())):
                fk = lmap.get(row.get("Field", "").strip())
                if fk: nc[fk] = row.get("Content", "")
            snapshot(); st.session_state.canvas = nc
            n = f.name.replace(".csv", "")
            st.session_state.file_name = n
            st.session_state.saved_files[n] = dict(nc)
            st.session_state.active_file = n
            return True, f"Loaded **{n}**"
        return False, "Unsupported format"
    except Exception as e:
        return False, str(e)

# ── COMPUTED VALUES ───────────────────────────────────────────
filled = sum(1 for f in ALL if st.session_state.canvas.get(f, "").strip())
total  = len(ALL)
pct    = int(filled / total * 100)
bmc_f  = sum(1 for f in BMC if st.session_state.canvas.get(f, "").strip())
vpc_f  = sum(1 for f in VPC if st.session_state.canvas.get(f, "").strip())
swot_f = sum(1 for f in SWOT if st.session_state.canvas.get(f, "").strip())

# ── READINESS SCORE ───────────────────────────────────────────
def compute_readiness():
    score = 0
    # Core canvas filled (max 40)
    core_fields = ["customer_segments", "value_propositions", "revenue_streams", "cost_structure",
                   "customer_jobs", "customer_pains", "customer_gains", "products_services"]
    score += sum(5 for f in core_fields if st.session_state.canvas.get(f, "").strip())
    # Supporting fields (max 20)
    sup_fields = ["channels", "customer_relationships", "key_activities", "key_resources"]
    score += sum(5 for f in sup_fields if st.session_state.canvas.get(f, "").strip())
    # SWOT (max 20)
    for f in SWOT:
        if st.session_state.canvas.get(f, "").strip():
            score += 5
    # Financial data entered
    if st.session_state.canvas.get("rev_price", "") or st.session_state.canvas.get("rev_volume", ""):
        score += 10
    # Founder info
    if st.session_state.get("founder_name", "").strip():
        score += 5
    if st.session_state.get("company_name", "").strip():
        score += 5
    return min(100, score)

readiness = compute_readiness()

# ── PLOTLY CHART FUNCTIONS ────────────────────────────────────
def chart_radar_completion():
    PD = PLOTLY_DARK if st.session_state.theme == "dark" else PLOTLY_LIGHT
    categories = ["Customer\nUnderstanding", "Value\nProposition", "Revenue\nModel",
                  "Go-to-Market", "Operations", "SWOT"]
    groups = [
        ["customer_segments","customer_jobs","customer_pains","customer_gains"],
        ["value_propositions","products_services","pain_relievers","gain_creators"],
        ["revenue_streams","cost_structure"],
        ["channels","customer_relationships"],
        ["key_activities","key_resources","key_partners"],
        ["swot_s","swot_w","swot_o","swot_t"],
    ]
    values = []
    for fields in groups:
        v = sum(1 for f in fields if st.session_state.canvas.get(f, "").strip())
        values.append(v / len(fields) * 100)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(0,212,170,0.25)',
        line=dict(color='#00d4aa', width=3),
        marker=dict(size=8, color='#00d4aa', line=dict(color='#fff', width=1)),
        name='Completion'
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(range=[0,100], gridcolor=PD['grid'], tickfont=dict(size=10,color=PD['text']),
                           ticksuffix='%'),
            angularaxis=dict(gridcolor=PD['grid'], tickfont=dict(size=11,color=PD['text']))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60,r=60,t=40,b=40),
        height=340,
        showlegend=False,
        font=dict(family='Outfit,Inter,sans-serif', color=PD['text'])
    )
    return fig

def chart_gauge_readiness():
    PD = PLOTLY_DARK if st.session_state.theme == "dark" else PLOTLY_LIGHT
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness,
        number={'font': {'size': 36, 'color': PD['text'], 'family': 'Outfit,Inter,sans-serif'}},
        domain={'x': [0,1], 'y': [0,1]},
        gauge={
            'axis': {'range': [0,100], 'tickwidth': 1, 'tickcolor': PD['grid']},
            'bar': {'color': '#00d4aa', 'thickness': 0.75},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 2, 'bordercolor': PD['grid'],
            'steps': [
                {'range': [0,33], 'color': 'rgba(224,82,82,0.15)'},
                {'range': [33,66], 'color': 'rgba(247,201,72,0.15)'},
                {'range': [66,100], 'color': 'rgba(62,207,142,0.15)'}
            ],
            'threshold': {'line': {'color': '#00d4aa', 'width': 3}, 'thickness': 0.8, 'value': readiness}
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=250, margin=dict(l=20,r=20,t=10,b=10),
        font=dict(family='Outfit,Inter,sans-serif')
    )
    return fig

def chart_category_bars():
    PD = PLOTLY_DARK if st.session_state.theme == "dark" else PLOTLY_LIGHT
    cats = ["BMC", "VPC", "SWOT"]
    vals = [bmc_f/9*100, vpc_f/6*100, swot_f/4*100]
    colors = ['#6c7fff', '#ff6b35', '#f7c948']
    fig = go.Figure()
    for i, (cat, val, col) in enumerate(zip(cats, vals, colors)):
        fig.add_trace(go.Bar(
            x=[cat], y=[val], name=cat,
            marker=dict(color=col, line=dict(color='rgba(255,255,255,0.2)', width=1)),
            text=[f'{int(val)}%'], textposition='outside',
            textfont=dict(size=14, color=PD['text'], family='Outfit,Inter'),
            width=0.5
        ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(0,0,0,0)', tickfont=dict(color=PD['text'])),
        yaxis=dict(gridcolor=PD['grid'], tickfont=dict(color=PD['text2']), ticksuffix='%', range=[0,110]),
        height=260, margin=dict(l=40,r=20,t=30,b=30),
        showlegend=False,
        font=dict(family='Outfit,Inter,sans-serif'),
        bargap=0.3
    )
    return fig

def chart_treemap_structure():
    PD = PLOTLY_DARK if st.session_state.theme == "dark" else PLOTLY_LIGHT
    labels = ["Canvas", "BMC", "VPC", "SWOT",
              "Key Partners", "Key Activities", "Value Props", "Relationships", "Segments",
              "Resources", "Channels", "Cost", "Revenue",
              "Cust Jobs", "Cust Pains", "Cust Gains", "Products", "Pain Relievers", "Gain Creators",
              "Strengths", "Weaknesses", "Opportunities", "Threats"]
    parents = ["", "Canvas", "Canvas", "Canvas",
               "BMC", "BMC", "BMC", "BMC", "BMC", "BMC", "BMC", "BMC", "BMC",
               "VPC", "VPC", "VPC", "VPC", "VPC", "VPC",
               "SWOT", "SWOT", "SWOT", "SWOT"]
    key_map = {
        "Key Partners":"key_partners", "Key Activities":"key_activities",
        "Value Props":"value_propositions", "Relationships":"customer_relationships",
        "Segments":"customer_segments", "Resources":"key_resources",
        "Channels":"channels", "Cost":"cost_structure", "Revenue":"revenue_streams",
        "Cust Jobs":"customer_jobs", "Cust Pains":"customer_pains", "Cust Gains":"customer_gains",
        "Products":"products_services", "Pain Relievers":"pain_relievers", "Gain Creators":"gain_creators",
        "Strengths":"swot_s", "Weaknesses":"swot_w", "Opportunities":"swot_o", "Threats":"swot_t"
    }
    values = [100, 55, 35, 10] + [10]*9 + [6]*6 + [3]*4
    colors_map = ["#55557a" if not st.session_state.canvas.get(key_map.get(l,""),"").strip() else
                  ("#3ecf8e" if l in ["Strengths","Opportunities"] else
                   "#e05252" if l in ["Weaknesses","Threats"] else
                   "#00d4aa" if l in ["Segments","Cust Jobs","Cust Pains","Cust Gains","Revenue","Channels","Relationships","Products"] else
                   "#ff6b35" if l in ["Value Props","Pain Relievers","Gain Creators","Key Activities"] else
                   "#6c7fff" if l in ["Key Partners","Resources"] else "#f7c948")
                  for l in labels]
    fig = go.Figure(go.Treemap(
        labels=labels, parents=parents, values=values,
        marker=dict(colors=colors_map, line=dict(color=PD['card'], width=2)),
        textfont=dict(size=12, color='white', family='Outfit,Inter'),
        hovertemplate='<b>%{label}</b><br>Parent: %{parent}<extra></extra>'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=340, margin=dict(l=10,r=10,t=10,b=10),
        font=dict(family='Outfit,Inter,sans-serif')
    )
    return fig

def chart_financial_waterfall(p, v, fc, vc_unit):
    PD = PLOTLY_DARK if st.session_state.theme == "dark" else PLOTLY_LIGHT
    revenue = p * v
    var_costs = vc_unit * v
    gross = revenue - var_costs
    profit = gross - fc

    fig = go.Figure(go.Waterfall(
        name="Financial Flow",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=["Revenue", "Variable<br>Costs", "Gross", "Fixed<br>Costs", "Net Profit"],
        y=[revenue, -var_costs, 0, -fc, profit],
        text=[f"₹{revenue:,}", f"-₹{var_costs:,}", "", f"-₹{fc:,}", f"₹{profit:,}"],
        textposition="outside",
        textfont=dict(size=12, color=PD['text']),
        connector={"line": {"color": PD['grid'], "width": 2}},
        increasing={"marker": {"color": "#3ecf8e"}},
        decreasing={"marker": {"color": "#e05252"}},
        totals={"marker": {"color": "#00d4aa" if profit >= 0 else "#e05252"}}
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=300, margin=dict(l=40,r=20,t=30,b=40),
        yaxis=dict(gridcolor=PD['grid'], tickfont=dict(color=PD['text2']), tickprefix="₹"),
        xaxis=dict(gridcolor='rgba(0,0,0,0)', tickfont=dict(color=PD['text'])),
        showlegend=False,
        font=dict(family='Outfit,Inter,sans-serif', color=PD['text'])
    )
    return fig

def chart_field_heatmap():
    PD = PLOTLY_DARK if st.session_state.theme == "dark" else PLOTLY_LIGHT
    all_fields = BMC + VPC + SWOT
    field_names = [PLAIN[f] for f in all_fields]
    statuses = [1 if st.session_state.canvas.get(f, "").strip() else 0 for f in all_fields]
    sections = (["BMC"]*9) + (["VPC"]*6) + (["SWOT"]*4)

    fig = go.Figure(data=go.Heatmap(
        z=[statuses],
        x=field_names,
        y=["Status"],
        colorscale=[[0, 'rgba(224,82,82,0.4)'], [1, 'rgba(62,207,142,0.6)']],
        showscale=False,
        text=[['✓' if s else '✗' for s in statuses]],
        texttemplate="%{text}",
        textfont=dict(size=16),
        hovertemplate='%{x}: %{z[0] ? "Filled" : "Empty"}<extra></extra>'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=120, margin=dict(l=40,r=10,t=10,b=80),
        xaxis=dict(tickangle=-45, tickfont=dict(size=9, color=PD['text2'])),
        yaxis=dict(visible=False),
        font=dict(family='Outfit,Inter,sans-serif')
    )
    return fig

# ── VPC SVG ───────────────────────────────────────────────────
def vpc_svg(size=300):
    def is_f(k): return bool(st.session_state.canvas.get(k, "").strip())
    def get_c(k): return ACCENT_MAP.get(COLORS[k]) if is_f(k) else T['bg3']
    c_ps, c_gc, c_pr = get_c("products_services"), get_c("gain_creators"), get_c("pain_relievers")
    c_cj, c_cg, c_cp = get_c("customer_jobs"), get_c("customer_gains"), get_c("customer_pains")
    a1, a2 = T['a1'], T['a2']
    return f"""<div style="display:flex;justify-content:center;width:100%"><svg viewBox="0 0 760 340" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:760px;height:auto"><defs><filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter><linearGradient id="g_v" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{a2}" stop-opacity="0.15"/><stop offset="100%" stop-color="{a2}" stop-opacity="0.05"/></linearGradient><linearGradient id="g_c" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{a1}" stop-opacity="0.15"/><stop offset="100%" stop-color="{a1}" stop-opacity="0.05"/></linearGradient></defs><g transform="translate(40,40)"><rect x="0" y="0" width="260" height="260" fill="url(#g_v)" stroke="{T['border']}" stroke-width="1.5" rx="8"/><path d="M 0 0 L 130 130 L 0 260 Z" fill="{c_ps}" opacity="0.85"/><path d="M 0 0 L 260 0 L 130 130 Z" fill="{c_gc}" opacity="0.85"/><path d="M 0 260 L 130 130 L 260 260 Z" fill="{c_pr}" opacity="0.85"/><line x1="0" y1="0" x2="260" y2="260" stroke="{T['border']}" stroke-width="1" opacity="0.4"/><line x1="0" y1="260" x2="260" y2="0" stroke="{T['border']}" stroke-width="1" opacity="0.4"/><text x="32" y="130" font-family="Outfit,sans-serif" font-size="11" font-weight="800" fill="white" transform="rotate(-90 32 130)" text-anchor="middle">PRODUCTS</text><text x="130" y="32" font-family="Outfit,sans-serif" font-size="11" font-weight="800" fill="white" text-anchor="middle">GAIN CREATORS</text><text x="130" y="238" font-family="Outfit,sans-serif" font-size="11" font-weight="800" fill="white" text-anchor="middle">PAIN RELIEVERS</text><rect x="110" y="110" width="40" height="40" rx="8" fill="{T['bg1']}" stroke="{a2}" stroke-width="2.5" filter="url(#glow)"/><text x="130" y="137" font-family="Outfit,sans-serif" font-size="20" font-weight="900" fill="{a2}" text-anchor="middle">V</text></g><g transform="translate(420,40)"><circle cx="170" cy="130" r="130" fill="url(#g_c)" stroke="{T['border']}" stroke-width="1.5"/><path d="M 170 0 L 300 130 L 170 260 Z" fill="{c_cj}" opacity="0.8"/><path d="M 170 0 L 170 260 L 40 130 Z" fill="{c_cg}" opacity="0.8"/><path d="M 40 130 L 170 260 L 300 130 Z" fill="{c_cp}" opacity="0.8"/><line x1="40" y1="130" x2="300" y2="130" stroke="{T['border']}" stroke-width="1" opacity="0.4"/><line x1="170" y1="0" x2="170" y2="260" stroke="{T['border']}" stroke-width="1" opacity="0.4"/><text x="240" y="130" font-family="Outfit,sans-serif" font-size="11" font-weight="800" fill="white" text-anchor="middle">JOBS</text><text x="120" y="75" font-family="Outfit,sans-serif" font-size="11" font-weight="800" fill="white" text-anchor="middle">GAINS</text><text x="120" y="185" font-family="Outfit,sans-serif" font-size="11" font-weight="800" fill="white" text-anchor="middle">PAINS</text><circle cx="170" cy="130" r="18" fill="{T['bg1']}" stroke="{a1}" stroke-width="2.5" filter="url(#glow)"/><text x="170" y="136" font-family="Outfit,sans-serif" font-size="16" font-weight="900" fill="{a1}" text-anchor="middle">C</text></g><text x="380" y="175" font-family="Outfit,sans-serif" font-size="28" fill="{T['text3']}" text-anchor="middle">⇄</text></svg></div>"""

# ── FIELD RENDERER ────────────────────────────────────────────
def field(key, height=130):
    color  = COLORS.get(key, "teal")
    accent = ACCENT_MAP.get(color, "var(--a1)")
    st.markdown(
        f'<div class="ccard {color}"><div class="ccard-title" style="color:{accent};">{LABELS[key]}</div></div>',
        unsafe_allow_html=True
    )
    val = st.text_area(
        LABELS[key], value=st.session_state.canvas[key],
        height=height, placeholder=HINTS[key],
        key=f"ta_{key}", label_visibility="collapsed"
    )
    if val != st.session_state.canvas[key]:
        snapshot()
        st.session_state.canvas[key] = val

def scard(key):
    color  = COLORS.get(key, "teal")
    accent = ACCENT_MAP.get(color, "var(--a1)")
    val    = st.session_state.canvas.get(key, "")
    content_html = (
        f'<div class="scard-val">{val}</div>' if val.strip()
        else '<div class="scard-empty">Not filled yet — add your thoughts</div>'
    )
    st.markdown(f"""
    <div class="scard" style="border-top:2.5px solid {accent};">
      <div class="scard-lbl" style="color:{accent};">{PLAIN[key]}</div>
      {content_html}
    </div>""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:14px 0 16px;border-bottom:1px solid var(--border);margin-bottom:18px;">
      <div style="font-size:0.72rem;color:var(--text3);letter-spacing:.16em;text-transform:uppercase;font-weight:600;">Canvas Studio Pro v5</div>
      <div style="font-size:1.3rem;font-weight:900;color:var(--text);margin-top:6px;letter-spacing:-0.02em;">🎯 Strategy Tools</div>
      <div style="font-size:0.78rem;color:var(--text3);margin-top:4px;">Premium Canvas Suite</div>
    </div>""", unsafe_allow_html=True)

    # Theme toggle
    th_label = "☀️ Switch to Light" if st.session_state.theme == "dark" else "🌙 Switch to Dark"
    if st.button(th_label, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # Founder info section
    st.markdown('<div style="font-size:0.70rem;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;margin-bottom:10px;font-weight:700;">👤 Founder Profile</div>', unsafe_allow_html=True)

    founder = st.text_input("Founder Name", value=st.session_state.founder_name, placeholder="Your name", label_visibility="collapsed", key="founder_input")
    if founder: st.session_state.founder_name = founder

    company = st.text_input("Company Name", value=st.session_state.company_name, placeholder="Company name", label_visibility="collapsed", key="company_input")
    if company: st.session_state.company_name = company

    st.markdown('<div style="border-top:1px solid var(--border);margin:16px 0 12px;"></div>', unsafe_allow_html=True)

    # Canvas name
    st.markdown('<div style="font-size:0.70rem;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;font-weight:700;">📝 Canvas Identity</div>', unsafe_allow_html=True)
    fname = st.text_input("Canvas Name", value=st.session_state.file_name, placeholder="e.g. startup_alpha_v1")
    if fname: st.session_state.file_name = fname.strip().replace(" ", "_")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save", use_container_width=True):
            save_canvas(st.session_state.file_name); st.toast("✅ Saved!", icon="💾")
    with c2:
        if st.button("↩ Undo", use_container_width=True): undo(); st.rerun()
    c3, c4 = st.columns(2)
    with c3:
        if st.button("🗑 Clear", use_container_width=True): clear_canvas(); st.toast("Canvas cleared")
    with c4:
        if st.button("💡 Tips", use_container_width=True):
            st.session_state.show_tips = not st.session_state.show_tips; st.rerun()

    if st.session_state.last_saved:
        st.markdown(f'<div style="font-size:0.78rem;color:var(--a1);text-align:center;margin:8px 0;">💾 Saved at {st.session_state.last_saved}</div>', unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid var(--border);margin:16px 0 12px;"></div>', unsafe_allow_html=True)

    # Export
    st.markdown('<div style="font-size:0.70rem;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;font-weight:700;">⬇️ Export</div>', unsafe_allow_html=True)
    nm = st.session_state.file_name
    st.download_button("📦 JSON", to_json(nm), f"{nm}.json", "application/json", use_container_width=True)
    st.download_button("📊 CSV",  to_csv(nm),  f"{nm}.csv",  "text/csv",         use_container_width=True)

    st.markdown('<div style="font-size:0.70rem;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;margin:14px 0 8px;font-weight:700;">🖨️ PDF Export</div>', unsafe_allow_html=True)
    pdf_size = st.selectbox("Paper Size", ["A4","A3","A5","Letter"], label_visibility="collapsed")
    pdf_orient = st.radio("Orientation", ["Landscape", "Portrait"], horizontal=True, label_visibility="collapsed")
    if st.button(f"📄 Generate PDF", use_container_width=True):
        pdf = to_pdf(nm, pdf_size, pdf_orient)
        if pdf:
            st.download_button(f"⬇️ Save {pdf_size} {pdf_orient} PDF", pdf, f"{nm}_{pdf_size}_{pdf_orient}.pdf", "application/pdf", use_container_width=True, key="pdl")
        else:
            st.error("Run: pip install reportlab")

    st.markdown('<div style="border-top:1px solid var(--border);margin:16px 0 12px;"></div>', unsafe_allow_html=True)

    # Import
    st.markdown('<div style="font-size:0.70rem;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;font-weight:700;">⬆️ Import</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload JSON or CSV", type=["json","csv"], label_visibility="collapsed")
    if up:
        ok, msg = load_upload(up)
        (st.success if ok else st.error)(msg)

    st.markdown('<div style="border-top:1px solid var(--border);margin:16px 0 12px;"></div>', unsafe_allow_html=True)

    # Saved canvases
    st.markdown('<div style="font-size:0.70rem;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;font-weight:700;">📁 Saved Canvases</div>', unsafe_allow_html=True)
    if not st.session_state.saved_files:
        st.markdown('<div style="font-size:0.85rem;color:var(--text3);">No saves yet.</div>', unsafe_allow_html=True)
    else:
        for fn in list(st.session_state.saved_files.keys()):
            icon = "🟢" if fn == st.session_state.active_file else "⚪"
            ac   = "act" if fn == st.session_state.active_file else ""
            st.markdown(f'<div class="fchip {ac}">{icon} {fn}</div>', unsafe_allow_html=True)
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Load", key=f"l_{fn}", use_container_width=True): load_canvas(fn); st.rerun()
            with cc2:
                if st.button("Del",  key=f"d_{fn}", use_container_width=True): delete_canvas(fn); st.rerun()

# ── HERO ──────────────────────────────────────────────────────
founder_display = st.session_state.get("founder_name", "") or "Guest Strategist"
company_display = st.session_state.get("company_name", "") or ""
name_display = st.session_state.file_name.replace("_", " ").title()

st.markdown(f"""
<div class="hero">
  <div style="flex:1;z-index:2;position:relative;">
    <div style="font-size:0.78rem;font-weight:700;color:var(--text3);letter-spacing:.16em;text-transform:uppercase;margin-bottom:6px;">Startup Strategy Toolkit</div>
    <div style="font-size:2.3rem;font-weight:900;color:var(--text);letter-spacing:-.04em;margin-bottom:8px;">🎯 {name_display}</div>
    <div style="font-size:0.88rem;color:var(--a6);font-weight:600;margin-bottom:12px;">
      👤 {founder_display} {f" · 🏢 {company_display}" if company_display else ""}
    </div>
    <div style="display:flex;align-items:center;gap:14px;">
      <span style="font-size:0.9rem;color:var(--text2);">{filled}/{total} fields complete</span>
      <div style="height:8px;width:200px;background:var(--bg3);border-radius:4px;overflow:hidden;box-shadow:inset 0 1px 3px rgba(0,0,0,0.3);">
        <div style="height:8px;width:{pct}%;background:linear-gradient(90deg,var(--a1),var(--green));border-radius:4px;transition:width .5s"></div>
      </div>
      <span style="font-size:0.95rem;font-weight:800;color:var(--a1);">{pct}%</span>
    </div>
  </div>
  <div style="text-align:right;z-index:2;position:relative;">
    <div style="display:flex;gap:9px;justify-content:flex-end;margin-bottom:10px;">
      <span class="float-badge" style="background:color-mix(in srgb,var(--a1) 15%,transparent);color:var(--a1);border:1px solid var(--a1);font-size:0.7rem;font-weight:800;padding:6px 14px;border-radius:8px;letter-spacing:.10em;font-family:'JetBrains Mono',monospace;">BMC</span>
      <span class="float-badge" style="background:color-mix(in srgb,var(--a2) 15%,transparent);color:var(--a2);border:1px solid var(--a2);font-size:0.7rem;font-weight:800;padding:6px 14px;border-radius:8px;letter-spacing:.10em;font-family:'JetBrains Mono',monospace;animation-delay:0.5s">VPC</span>
      <span class="float-badge" style="background:color-mix(in srgb,var(--a3) 12%,transparent);color:var(--a3);border:1px solid var(--border2);font-size:0.7rem;font-weight:800;padding:6px 14px;border-radius:8px;letter-spacing:.10em;font-family:'JetBrains Mono',monospace;animation-delay:1s">{T['mode_name']}</span>
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.74rem;color:var(--text3);">{datetime.now().strftime("%d %b %Y  ·  %H:%M")}</div>
    <div style="margin-top:8px;font-size:0.78rem;color:var(--a1);font-weight:700;">📊 Readiness: {readiness}%</div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.show_tips:
    st.markdown("""<div class="tipbox">
      💡 <b>Pro Tips:</b> Start with <b style="color:var(--a1)">Customer Segments</b> → then <b style="color:var(--a1)">Value Propositions</b> → work outward.
      The VPC circle fills in real time. Use <b>Tab</b> to jump between fields. Save often.
    </div>""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────
t1, t2, t3, t4, t5, t6 = st.tabs([
    "📋 Business Model Canvas",
    "🔵 Value Proposition Canvas",
    "🔀 Full Overview",
    "✨ Insights & Visuals",
    "📈 SWOT & Revenue",
    "📊 Analytics Dashboard"
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — BMC
# ════════════════════════════════════════════════════════════════
with t1:
    st.markdown('<div class="ibanner">📋 <b>Business Model Canvas</b> — 9 building blocks describing how your business creates, delivers, and captures value. Fill each section to build a complete picture.</div>', unsafe_allow_html=True)

    # Row 1
    r1_col1, r1_col2, r1_col3 = st.columns(3)
    with r1_col1: field("key_partners", 220)
    with r1_col2: field("key_activities", 220)
    with r1_col3: field("value_propositions", 220)
    
    # Row 2
    r2_col1, r2_col2, r2_col3 = st.columns(3)
    with r2_col1: field("key_resources", 220)
    with r2_col2: field("customer_relationships", 220)
    with r2_col3: field("customer_segments", 220)
    
    # Row 3
    r3_col1, r3_col2, r3_col3 = st.columns(3)
    with r3_col1: field("channels", 220)
    with r3_col2: field("cost_structure", 220)
    with r3_col3: field("revenue_streams", 220)

    st.markdown('<hr class="sdiv">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — VPC
# ════════════════════════════════════════════════════════════════
with t2:
    st.markdown(f'<div class="ibanner" style="border-left-color:var(--a2);">🔵 <b>Value Proposition Canvas</b> — Match your offer to what customers need. <b style="color:var(--a1)">Teal ring</b> = Customer Profile · <b style="color:var(--a2)">Orange ring</b> = Value Map. Circle fills as you type.</div>', unsafe_allow_html=True)

    cVM, cCIR, cCP = st.columns([1.2, 4.5, 1.2])
    with cVM:
        st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a2);letter-spacing:.13em;text-transform:uppercase;margin-bottom:14px;">📦 Value Map</div>', unsafe_allow_html=True)
        field("products_services", 120)
        field("gain_creators", 120)
        field("pain_relievers", 120)
    with cCIR:
        st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
        st.markdown(vpc_svg(), unsafe_allow_html=True)
    with cCP:
        st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a1);letter-spacing:.13em;text-transform:uppercase;margin-bottom:14px;">👤 Customer Profile</div>', unsafe_allow_html=True)
        field("customer_jobs", 120)
        field("customer_gains", 120)
        field("customer_pains", 120)

# ════════════════════════════════════════════════════════════════
# TAB 3 — FULL OVERVIEW
# ════════════════════════════════════════════════════════════════
with t3:
    st.markdown("### 🔀 Full Canvas Overview")
    st.markdown("""<div style="font-size:0.94rem;color:var(--text2);margin-bottom:20px;">Read-only bird's-eye view of both canvases. Edit in the tabs above. Charts update in real-time.</div>""", unsafe_allow_html=True)

    # Metrics with Plotly gauge
    m1, m2, m3, m4, m5 = st.columns(5)
    metrics = [
        (m1, f"{pct}%", "Complete", "var(--a1)"),
        (m2, f"{bmc_f}/9", "BMC Fields", "var(--a3)"),
        (m3, f"{vpc_f}/6", "VPC Fields", "var(--a2)"),
        (m4, f"{swot_f}/4", "SWOT Fields", "var(--a4)"),
        (m5, f"{readiness}", "Readiness", "var(--green)"),
    ]
    for col, val, label, color in metrics:
        with col:
            st.markdown(f'<div class="mbox"><p class="mval" style="color:{color};">{val}</p><p class="mlbl">{label}</p></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # Progress with animated gradient
    st.progress(filled / total)
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    # Category bar chart
    if PLOTLY_OK:
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(chart_category_bars(), use_container_width=True, config={'displayModeBar': False}, key="chart_cat_main")
        st.markdown('</div>', unsafe_allow_html=True)

    # BMC overview - 3x3 Grid
    st.markdown(f'<div style="font-size:0.82rem;font-weight:800;color:var(--a3);letter-spacing:.12em;text-transform:uppercase;margin-bottom:14px;">📋 Business Model Canvas</div>', unsafe_allow_html=True)
    
    # Row 1
    r1_col1, r1_col2, r1_col3 = st.columns(3)
    with r1_col1: scard("key_partners")
    with r1_col2: scard("key_activities")
    with r1_col3: scard("value_propositions")
    
    # Row 2
    r2_col1, r2_col2, r2_col3 = st.columns(3)
    with r2_col1: scard("key_resources")
    with r2_col2: scard("customer_relationships")
    with r2_col3: scard("customer_segments")
    
    # Row 3
    r3_col1, r3_col2, r3_col3 = st.columns(3)
    with r3_col1: scard("channels")
    with r3_col2: scard("cost_structure")
    with r3_col3: scard("revenue_streams")

    st.markdown('<hr class="sdiv">', unsafe_allow_html=True)

    # VPC overview
    st.markdown(f'<div style="font-size:0.82rem;font-weight:800;color:var(--a2);letter-spacing:.12em;text-transform:uppercase;margin-bottom:14px;">🔵 Value Proposition Canvas</div>', unsafe_allow_html=True)
    vc1, vc2, vc3 = st.columns([2, 1.8, 2])
    with vc1:
        for k in ["products_services","pain_relievers","gain_creators"]: scard(k)
    with vc2:
        st.markdown(vpc_svg(), unsafe_allow_html=True)
    with vc3:
        for k in ["customer_jobs","customer_pains","customer_gains"]: scard(k)

    st.markdown('<hr class="sdiv">', unsafe_allow_html=True)

    # SWOT overview
    st.markdown(f'<div style="font-size:0.82rem;font-weight:800;color:var(--a4);letter-spacing:.12em;text-transform:uppercase;margin-bottom:14px;">📊 SWOT Analysis</div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        scard("swot_s"); scard("swot_o")
    with sc2:
        scard("swot_w"); scard("swot_t")

    st.markdown('<hr class="sdiv">', unsafe_allow_html=True)

    # Field completion status
    if PLOTLY_OK:
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.82rem;font-weight:800;color:var(--a6);letter-spacing:.12em;text-transform:uppercase;margin-bottom:10px;">🎯 Field Completion Heatmap</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_field_heatmap(), use_container_width=True, config={'displayModeBar': False}, key="chart_heatmap_main")
        st.markdown('</div>', unsafe_allow_html=True)

    # Status message
    if pct == 100:
        st.success("🎉 100% complete — ready to pitch and validate!")
    elif pct >= 70:
        st.info("📝 Strong progress — close to a complete canvas.")
    elif pct >= 40:
        st.warning("🚧 Halfway — focus on Value Propositions and Customer Segments.")
    else:
        st.error("🔴 Early stage — start with Customer Segments, then Value Propositions.")

# ════════════════════════════════════════════════════════════════
# TAB 4 — INSIGHTS & VISUALS (with Plotly)
# ════════════════════════════════════════════════════════════════
with t4:
    st.markdown("### ✨ Insights & Visual Dashboard")

    # Top row: Radar + Gauge side by side
    if PLOTLY_OK:
        r1c1, r1c2 = st.columns([2, 1])
        with r1c1:
            st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a3);letter-spacing:.11em;text-transform:uppercase;margin-bottom:10px;">📊 Canvas Strength Radar</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_radar_completion(), use_container_width=True, config={'displayModeBar': False}, key="chart_radar_insights")
            st.markdown('</div>', unsafe_allow_html=True)
        with r1c2:
            st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a1);letter-spacing:.11em;text-transform:uppercase;margin-bottom:10px;">🎯 Readiness Score</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_gauge_readiness(), use_container_width=True, config={'displayModeBar': False}, key="chart_gauge_insights")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Fallback: Radar Bars
        st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a3);letter-spacing:.11em;text-transform:uppercase;margin-bottom:14px;">📊 Canvas Strength Radar</div>', unsafe_allow_html=True)
        GROUPS = [
            ("Customer Understanding", ["customer_segments","customer_jobs","customer_pains","customer_gains"], T['a1']),
            ("Value Proposition",      ["value_propositions","products_services","pain_relievers","gain_creators"], T['a2']),
            ("Revenue Model",          ["revenue_streams","cost_structure"], T['a4']),
            ("Go-to-Market",           ["channels","customer_relationships"], T['a1']),
            ("Operations",             ["key_activities","key_resources","key_partners"], T['a3']),
        ]
        st.markdown('<div class="radar-wrap">', unsafe_allow_html=True)
        for label, fields, color in GROUPS:
            score   = sum(1 for f in fields if st.session_state.canvas.get(f, "").strip())
            pct_g   = score / len(fields)
            bar_w   = int(pct_g * 100)
            icon    = "🟢" if pct_g == 1 else ("🟡" if pct_g >= 0.5 else "🔴")
            st.markdown(f"""
            <div class="rbar-row">
              <div class="rbar-lbl">{icon} {label}</div>
              <div class="rbar-track">
                <div class="rbar-fill" style="width:{bar_w}%;background:linear-gradient(90deg,{color},{color}88)"></div>
              </div>
              <div class="rbar-pct">{score}/{len(fields)}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)

    # VPC Fit Diagram
    st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a3);letter-spacing:.11em;text-transform:uppercase;margin-bottom:14px;">🔵 VPC Fit Diagram</div>', unsafe_allow_html=True)

    r1c, r2c = st.columns([1, 1.6])
    with r1c:
        st.markdown(vpc_svg(), unsafe_allow_html=True)
    with r2c:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        fit_items = [
            ("Customer Jobs → Products",  "customer_jobs",  "products_services", "🧑‍💼 → 🛠️"),
            ("Pain → Pain Reliever",       "customer_pains", "pain_relievers",    "😣 → 🩹"),
            ("Gain → Gain Creator",        "customer_gains", "gain_creators",     "😊 → 🎁"),
        ]
        for label, cf, vf, arrow in fit_items:
            c_ok  = bool(st.session_state.canvas.get(cf, "").strip())
            v_ok  = bool(st.session_state.canvas.get(vf, "").strip())
            both  = c_ok and v_ok
            sc    = T['green'] if both else (T['a4'] if (c_ok or v_ok) else T['red'])
            stxt  = "✅ Matched" if both else ("⚡ Partial" if (c_ok or v_ok) else "❌ Empty")
            st.markdown(f"""
            <div class="fitcard">
              <div class="fitcard-arrow">{arrow} {label}</div>
              <div class="fitcard-status" style="color:{sc};">{stxt}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="sdiv">', unsafe_allow_html=True)

    # Strategic Checklist
    st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a1);letter-spacing:.11em;text-transform:uppercase;margin-bottom:14px;">📋 Strategic Readiness Checklist</div>', unsafe_allow_html=True)

    checks = [
        ("Have you defined WHO exactly your customer is?",          bool(st.session_state.canvas["customer_segments"].strip())),
        ("Do you know their top pains?",                            bool(st.session_state.canvas["customer_pains"].strip())),
        ("Is your Value Proposition specific (not generic)?",       bool(st.session_state.canvas["value_propositions"].strip())),
        ("Does your Pain Reliever directly match customer pains?",  bool(st.session_state.canvas["pain_relievers"].strip() and st.session_state.canvas["customer_pains"].strip())),
        ("Do your Gain Creators match what customers want?",        bool(st.session_state.canvas["gain_creators"].strip() and st.session_state.canvas["customer_gains"].strip())),
        ("Do you have a clear Revenue Model?",                      bool(st.session_state.canvas["revenue_streams"].strip())),
        ("Have you mapped your main Cost Drivers?",                 bool(st.session_state.canvas["cost_structure"].strip())),
        ("Do you know how you'll reach customers (Channels)?",      bool(st.session_state.canvas["channels"].strip())),
        ("Have you identified your Key Partners?",                  bool(st.session_state.canvas["key_partners"].strip())),
        ("Have you completed the SWOT analysis?",                    all(st.session_state.canvas[f].strip() for f in SWOT)),
    ]
    score = sum(1 for _, v in checks if v)
    ccol1, ccol2 = st.columns([3, 1])
    with ccol1:
        for q, passed in checks:
            icon  = "✅" if passed else "⬜"
            color = T['green'] if passed else T['text3']
            st.markdown(f'<div class="chk" style="color:{color};">{icon} &nbsp;{q}</div>', unsafe_allow_html=True)
    with ccol2:
        st.markdown(f"""
        <div style="background:var(--glass);backdrop-filter:blur(16px);border:1px solid var(--border);border-radius:14px;padding:24px;text-align:center;">
          <div style="font-size:0.75rem;color:var(--text3);text-transform:uppercase;letter-spacing:.12em;margin-bottom:10px;">Checklist Score</div>
          <div style="font-size:3rem;font-weight:900;color:var(--a1);margin:10px 0;">{score}</div>
          <div style="font-size:1rem;color:var(--text3);">/ {len(checks)}</div>
          <div style="height:8px;width:100%;background:var(--bg3);border-radius:4px;margin-top:16px;overflow:hidden;">
            <div style="height:100%;width:{int(score/len(checks)*100)}%;background:linear-gradient(90deg,var(--a1),var(--green));border-radius:4px;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="sdiv">', unsafe_allow_html=True)

    # ── Hypotheses & Notes ────────────────────────────────────
    st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a4);letter-spacing:.11em;text-transform:uppercase;margin-bottom:12px;">📝 Hypotheses & Risk Tracker</div>', unsafe_allow_html=True)

    notes_col1, notes_col2 = st.columns([2, 1])
    with notes_col1:
        st.text_area(
            "Notes", height=130,
            placeholder="e.g. Hypothesis: Customers will pay ₹999/mo · Risk: Low brand awareness · Next: 10 customer discovery calls",
            key="canvas_notes", label_visibility="collapsed"
        )
    with notes_col2:
        # Risk assessment mini-card
        risk_level = "🔴 High Risk" if score < 4 else ("🟡 Medium Risk" if score < 7 else "🟢 Low Risk")
        risk_color = T['red'] if score < 4 else (T['a4'] if score < 7 else T['green'])
        st.markdown(f"""
        <div style="background:var(--glass);backdrop-filter:blur(16px);border:1px solid var(--border);border-radius:14px;padding:18px;text-align:center;">
          <div style="font-size:0.72rem;color:var(--text3);text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px;">Current Risk Level</div>
          <div style="font-size:1.2rem;font-weight:800;color:{risk_color};margin:8px 0;">{risk_level}</div>
          <div style="font-size:0.82rem;color:var(--text2);margin-top:8px;">{'Critical gaps remain' if score < 4 else 'Some validation needed' if score < 7 else 'Strong foundation'}</div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 5 — SWOT & REVENUE
# ════════════════════════════════════════════════════════════════
with t5:
    st.markdown("### 📈 SWOT Analysis & Financial Estimator")

    st.markdown(f'<div style="font-size:0.82rem;font-weight:800;color:var(--a3);letter-spacing:.11em;text-transform:uppercase;margin-bottom:14px;">📋 SWOT Matrix</div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        field("swot_s", 130)
        field("swot_o", 130)
    with sc2:
        field("swot_w", 130)
        field("swot_t", 130)

    st.markdown('<hr class="sdiv">', unsafe_allow_html=True)

    # Financial estimator with Plotly waterfall
    st.markdown(f'<div style="font-size:0.82rem;font-weight:800;color:var(--a1);letter-spacing:.11em;text-transform:uppercase;margin-bottom:14px;">💰 Financial Quick-Estimator</div>', unsafe_allow_html=True)

    fe1, fe2, fe3 = st.columns([1, 1, 1.5])
    with fe1:
        p = st.number_input("Avg Price (₹)", value=1000, step=100)
        v = st.number_input("Monthly Volume", value=100, step=10)
    with fe2:
        fc = st.number_input("Fixed Costs/mo (₹)", value=50000, step=5000)
        vc_unit = st.number_input("Variable Cost/unit (₹)", value=200, step=50)

    rev = p * v
    cos = fc + (vc_unit * v)
    pro = rev - cos
    mar = (pro / rev * 100) if rev > 0 else 0

    with fe3:
        st.markdown(f"""
        <div class="mbox" style="background:var(--bg2);text-align:left;padding:20px;">
          <div style="font-size:0.8rem;color:var(--text3);text-transform:uppercase;letter-spacing:.10em;margin-bottom:6px;">Monthly Estimate</div>
          <div style="font-size:1.9rem;font-weight:900;color:var(--text);margin:6px 0;">₹{pro:,} <span style="font-size:0.95rem;color:{T['green'] if pro>0 else T['red']};">{"+" if pro>0 else ""}{int(mar)}% margin</span></div>
          <div style="font-size:0.88rem;color:var(--text2);">Revenue: ₹{rev:,} &nbsp;·&nbsp; Total Cost: ₹{cos:,}</div>
          <div style="height:8px;width:100%;background:var(--bg3);border-radius:4px;margin-top:14px;overflow:hidden;">
            <div style="height:100%;width:{min(100, max(0, int(mar*2))) if pro>0 else 0}%;background:linear-gradient(90deg,var(--green),var(--a1));border-radius:4px;"></div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Waterfall chart
    if PLOTLY_OK:
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a1);letter-spacing:.11em;text-transform:uppercase;margin-bottom:10px;">📊 P&L Waterfall</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_financial_waterfall(p, v, fc, vc_unit), use_container_width=True, config={'displayModeBar': False}, key="chart_waterfall")
        st.markdown('</div>', unsafe_allow_html=True)

    if pro < 0:
        be = int(fc / (p - vc_unit)) if p > vc_unit else "∞"
        st.warning(f"⚠️ You are currently losing money. Break-even requires **{be}** units/mo.")
    elif pro > 0:
        st.success("✅ Profitable model! Focus on scaling volume or reducing unit costs.")

# ════════════════════════════════════════════════════════════════
# TAB 6 — ANALYTICS DASHBOARD (NEW)
# ════════════════════════════════════════════════════════════════
with t6:
    st.markdown("### 📊 Canvas Analytics Dashboard")
    st.markdown('<div style="font-size:0.94rem;color:var(--text2);margin-bottom:20px;">Premium visual analytics for your business canvas. Track completion, identify gaps, and measure strategic readiness in real-time.</div>', unsafe_allow_html=True)

    if not PLOTLY_OK:
        st.error("⚠️ Plotly not installed. Run `pip install plotly` to enable interactive charts.")
    else:
        # Row 1: Gauge + Category bars
        d1, d2 = st.columns([1, 2])
        with d1:
            st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a1);letter-spacing:.11em;text-transform:uppercase;margin-bottom:10px;">🎯 Overall Readiness</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_gauge_readiness(), use_container_width=True, config={'displayModeBar': False}, key="chart_gauge_dash")
            # Readiness breakdown
            st.markdown(f"""
            <div style="font-size:0.82rem;color:var(--text2);margin-top:10px;">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span>Core Fields</span><span style="color:var(--a1);font-weight:700;">{'✓ Complete' if all(st.session_state.canvas.get(f,'').strip() for f in ['customer_segments','value_propositions','revenue_streams']) else '⚠️ Incomplete'}</span></div>
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span>SWOT Done</span><span style="color:var(--a1);font-weight:700;">{'✓ Yes' if all(st.session_state.canvas.get(f,'').strip() for f in SWOT) else '⚠️ Pending'}</span></div>
              <div style="display:flex;justify-content:space-between;"><span>Founder Profile</span><span style="color:var(--a1);font-weight:700;">{'✓ Set' if st.session_state.get('founder_name','') else '⚠️ Missing'}</span></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with d2:
            st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a3);letter-spacing:.11em;text-transform:uppercase;margin-bottom:10px;">📊 Completion by Category</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_category_bars(), use_container_width=True, config={'displayModeBar': False}, key="chart_cat_dash")
            st.markdown('</div>', unsafe_allow_html=True)

        # Row 2: Radar chart
        st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a3);letter-spacing:.11em;text-transform:uppercase;margin-bottom:10px;">📊 Strategic Dimension Radar</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.85rem;color:var(--text2);margin-bottom:10px;">Visualize your canvas strength across 6 strategic dimensions. A balanced shape indicates a well-rounded strategy.</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_radar_completion(), use_container_width=True, config={'displayModeBar': False}, key="chart_radar_dash")
        st.markdown('</div>', unsafe_allow_html=True)

        # Row 3: Treemap + Heatmap
        t1, t2 = st.columns([1, 1])
        with t1:
            st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a4);letter-spacing:.11em;text-transform:uppercase;margin-bottom:10px;">🗺️ Canvas Structure Map</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_treemap_structure(), use_container_width=True, config={'displayModeBar': False}, key="chart_treemap_dash")
            st.markdown('</div>', unsafe_allow_html=True)
        with t2:
            st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.78rem;font-weight:800;color:var(--a6);letter-spacing:.11em;text-transform:uppercase;margin-bottom:10px;">🎯 Field Completion Status</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_field_heatmap(), use_container_width=True, config={'displayModeBar': False}, key="chart_heatmap_dash")
            st.markdown('</div>', unsafe_allow_html=True)

        # Row 4: AI Power Prompts (enhanced)
        st.markdown('<hr class="sdiv">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.82rem;font-weight:800;color:var(--a5);letter-spacing:.11em;text-transform:uppercase;margin-bottom:14px;">🤖 AI Strategy Prompts (Copy & Paste into ChatGPT/Claude)</div>', unsafe_allow_html=True)

        prompts = [
            ("Customer Discovery Interview", f"Based on this customer profile: Jobs=[{st.session_state.canvas.get('customer_jobs','')[:80]}], Pains=[{st.session_state.canvas.get('customer_pains','')[:80]}], Gains=[{st.session_state.canvas.get('customer_gains','')[:80]}], write 5 discovery interview questions to validate assumptions."),
            ("Pitch Deck Outline", f"Create a 10-slide pitch deck outline for [{st.session_state.file_name}] with Value Proposition: [{st.session_state.canvas.get('value_propositions','')[:100]}], Target: [{st.session_state.canvas.get('customer_segments','')[:80]}], Revenue: [{st.session_state.canvas.get('revenue_streams','')[:80]}]."),
            ("Competitive Analysis", f"Analyze competitors for a business with these characteristics: Value Prop=[{st.session_state.canvas.get('value_propositions','')[:80]}], Channels=[{st.session_state.canvas.get('channels','')[:80]}]. Suggest 3 direct and 3 indirect competitors."),
            ("Go-to-Market Strategy", f"Design a GTM strategy for: Product=[{st.session_state.canvas.get('products_services','')[:80]}], Segments=[{st.session_state.canvas.get('customer_segments','')[:80]}], Channels=[{st.session_state.canvas.get('channels','')[:80]}], Relationships=[{st.session_state.canvas.get('customer_relationships','')[:80]}]. Include a 90-day launch timeline."),
            ("Risk Mitigation Plan", f"Given this SWOT - Strengths:[{st.session_state.canvas.get('swot_s','')[:60]}], Weaknesses:[{st.session_state.canvas.get('swot_w','')[:60]}], Threats:[{st.session_state.canvas.get('swot_t','')[:60]}], create a risk mitigation matrix with top 5 risks and mitigation strategies."),
        ]
        for title, prompt_text in prompts:
            with st.expander(f"📋 {title}"):
                st.code(prompt_text, language=None)
                st.button(f"📋 Copy", key=f"cp_{title}", on_click=lambda t=prompt_text: st.write(t))

        # Footer
        st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center;padding:20px;color:var(--text3);font-size:0.78rem;border-top:1px solid var(--border);margin-top:20px;">
          <div style="font-weight:700;letter-spacing:.10em;text-transform:uppercase;margin-bottom:4px;">Canvas Studio Pro v5</div>
          <div>Premium Strategy Toolkit · {datetime.now().strftime("%d %b %Y")}</div>
        </div>
        """, unsafe_allow_html=True)
