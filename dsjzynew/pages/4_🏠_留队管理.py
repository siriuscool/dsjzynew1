import streamlit as st
from utils.style import apply_dark_theme
from src.auth import check_login
from src.stay import apply_stay, get_stays

st.set_page_config(page_title="留队管理", page_icon="🏠", layout="wide")
apply_dark_theme()
u = check_login()
st.markdown('<div class="neon-title">🏠 留队管理</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2 = st.tabs(["📋 留队记录", "➕ 申请留队"])
with t1:
    df = get_stays()
    if df.empty: st.info("暂无留队记录")
    else: st.dataframe(df, use_container_width=True, hide_index=True)
with t2:
    st.subheader("申请留队")
    d = st.date_input("留队日期")
    reason = st.selectbox("留队原因", ["周末留队","节假日留队","值班","其他"])
    act = st.selectbox("留队活动", ["自习","训练","值班","休息"])
    if st.button("提交申请"):
        apply_stay(u["id"], str(d), reason, act)
        st.success("留队申请已提交"); st.rerun()
