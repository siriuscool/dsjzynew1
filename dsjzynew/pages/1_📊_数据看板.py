import streamlit as st
from utils.style import apply_dark_theme, glass_card
from src.auth import check_login, require_level
from src.stats import get_overview, leave_trend, leave_by_reason, platoon_compare, duty_by_task
import plotly.express as px

st.set_page_config(page_title="数据看板", page_icon="📊", layout="wide")
apply_dark_theme()
check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">📊 数据看板</div>', unsafe_allow_html=True)
st.markdown("---")

s = get_overview()
c = st.columns(6)
glass_card(c[0], "总人数", s["总人数"], "👥")
glass_card(c[1], "在队", s["在队"], "✅")
glass_card(c[2], "请假中", s["请假中"], "📝")
glass_card(c[3], "外出中", s["外出中"], "🚪")
glass_card(c[4], "留队", s["留队"], "🏠")
glass_card(c[5], "任务", s["公差"], "🔧")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    df = leave_trend()
    if not df.empty:
        st.plotly_chart(px.line(df, x="date", y="count", markers=True, title="请假趋势"), use_container_width=True)
with col2:
    df = leave_by_reason()
    if not df.empty:
        st.plotly_chart(px.pie(df, names="reason", values="count", hole=0.4, title="请假事由分布"), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    df = platoon_compare()
    if not df.empty:
        st.plotly_chart(px.bar(df, x="platoon", y="请假次数", color="请假次数", color_continuous_scale="Blues", title="各派请假对比"), use_container_width=True)
with col2:
    df = duty_by_task()
    if not df.empty:
        st.plotly_chart(px.bar(df, x="task_name", y="count", color="count", color_continuous_scale="Sunset", title="任务类型分布"), use_container_width=True)
