import streamlit as st
from utils.style import apply_dark_theme, glass_card, sub_title
from src.auth import check_login, require_level
from src.mapreduce_log import mapreduce_analyze
from src.spark_analyze import spark_analyze
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="大数据分析", page_icon="⚡", layout="wide")
apply_dark_theme()
check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">⚡ 大数据分析引擎</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#9ab;">MapReduce 分布式思想 + PySpark 计算</p>', unsafe_allow_html=True)
st.markdown("---")

sub_title("🔷 MapReduce 行为分析")
if st.button("🚀 运行 MapReduce 分析", use_container_width=True):
    with st.spinner("Map → Shuffle → Reduce 执行中..."):
        r = mapreduce_analyze()
    c = st.columns(4)
    glass_card(c[0], "总记录数", f"{r['total_rows']:,}", "📊")
    glass_card(c[1], "Map耗时", f"{r['map_time']}s", "⚙️")
    glass_card(c[2], "Shuffle耗时", f"{r['shuffle_time']}s", "🔀")
    glass_card(c[3], "Reduce耗时", f"{r['reduce_time']}s", "📉")
    st.markdown("---")
    df = pd.DataFrame(list(r["result"].items()), columns=["行为类型","次数"])
    fig = px.bar(df, x="行为类型", y="次数", color="次数", color_continuous_scale="Turbo", text="次数", title="MapReduce 统计结果")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
sub_title("🔶 PySpark 分布式分析")
if st.button("⚡ 运行 PySpark 分析", use_container_width=True):
    with st.spinner("PySpark 运行中..."):
        r = spark_analyze()
    if "error" in r:
        st.warning(r["error"]); st.info("未安装PySpark不影响其他功能。")
    else:
        c = st.columns(2)
        glass_card(c[0], "总记录数", f"{r['total']:,}", "📊")
        glass_card(c[1], "Spark耗时", f"{r['elapsed']}s", "⚡")
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(r["action_dist"], names="action", values="count", hole=0.4, title="行为类型分布"), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(r["location_dist"], x="location", y="count", color="count", color_continuous_scale="Sunset", title="地点分布"), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.bar(r["cadet_dist"], x="cadet_id", y="count", color="count", color_continuous_scale="Blues", title="各学员行为次数"), use_container_width=True)
        with c2:
            st.plotly_chart(px.line(r["hour_dist"], x="hour", y="count", markers=True, title="24小时行为分布"), use_container_width=True)
