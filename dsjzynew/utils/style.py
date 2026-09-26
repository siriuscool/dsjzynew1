import streamlit as st

def apply_dark_theme():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg,#0f0c29,#302b63,#24243e); color:#eee; }
    .neon-title { font-size:42px; font-weight:900; text-align:center;
        background: linear-gradient(90deg,#00f2fe,#4facfe,#00f2fe);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        text-shadow:0 0 30px rgba(79,172,254,0.5); letter-spacing:2px; }
    .glass-card { background:rgba(255,255,255,0.08); backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.15); border-radius:18px;
        padding:22px; text-align:center; box-shadow:0 8px 32px rgba(0,0,0,0.3);
        transition:all 0.3s; }
    .glass-card:hover { transform:translateY(-6px); border-color:#4facfe;
        box-shadow:0 12px 40px rgba(79,172,254,0.4); }
    .glass-card .label { font-size:14px; color:#9ab; }
    .glass-card .value { font-size:30px; font-weight:bold;
        background: linear-gradient(90deg,#00f2fe,#4facfe);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    [data-testid="stSidebar"] { background:rgba(15,12,41,0.95);
        border-right:1px solid rgba(79,172,254,0.2); }
    </style>""", unsafe_allow_html=True)

def glass_card(col, label, value, icon=""):
    col.markdown(f"""<div class="glass-card">
        <div class="label">{icon} {label}</div>
        <div class="value">{value}</div></div>""", unsafe_allow_html=True)

def sub_title(text):
    st.markdown(f'<h3 style="color:#4facfe;border-left:4px solid #4facfe;'
                f'padding-left:12px;margin:20px 0 10px 0;">{text}</h3>',
                unsafe_allow_html=True)
