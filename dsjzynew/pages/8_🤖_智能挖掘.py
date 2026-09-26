import streamlit as st
from utils.style import apply_dark_theme, glass_card, sub_title
from src.auth import check_login, require_level
from src.ml_cluster import build_cadet_features, cluster_cadets
from src.predict import daily_leave_trend, predict_next_days
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="智能挖掘", page_icon="🤖", layout="wide")
apply_dark_theme()
check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">🤖 智能数据挖掘</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#9ab;">KMeans 聚类 · 线性回归预测</p>', unsafe_allow_html=True)
st.markdown("---")

sub_title("🔮 学员行为聚类（KMeans）")
if st.button("🎯 运行聚类分析", use_container_width=True):
    with st.spinner("正在聚类..."):
        df = build_cadet_features()
        clustered, summary = cluster_cadets(df, n_clusters=3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(summary.iterrows()):
        glass_card(cols[i], row["群体名称"], f"{int(row['人数'])}人", "👥")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.scatter(clustered, x="请假次数", y="外出次数", color="群体名称", size="总行为", hover_data=["cadet_id"], title="学员群体分布（请假 vs 外出）", color_discrete_sequence=px.colors.qualitative.Set2), use_container_width=True)
    with c2:
        st.plotly_chart(px.scatter(clustered, x="任务次数", y="超时次数", color="群体名称", size="总行为", hover_data=["cadet_id"], title="学员群体分布（任务 vs 超时）", color_discrete_sequence=px.colors.qualitative.Set2), use_container_width=True)
    sub_title("各群体特征对比")
    st.dataframe(summary, use_container_width=True)
    sub_title("学员明细")
    st.dataframe(clustered, use_container_width=True, hide_index=True)

st.markdown("---")
sub_title("📈 请假趋势预测（线性回归）")
if st.button("🔮 预测未来7天请假趋势", use_container_width=True):
    with st.spinner("正在预测..."):
        df = daily_leave_trend()
        result = predict_next_days(df, days=7)
    if result is None: st.warning("数据不足")
    else:
        pred, r2 = result
        c1, c2 = st.columns(2)
        glass_card(c1, "预测天数", "7天", "📅")
        glass_card(c2, "模型拟合度 R²", f"{r2}", "📊")
        st.markdown("---")
        hist = df.tail(30).copy(); hist["类型"] = "历史"
        p = pred.copy(); p.columns = ["date","count"]; p["类型"] = "预测"
        combined = pd.concat([hist, p])
        fig = px.line(combined, x="date", y="count", color="类型", markers=True, title="请假趋势（历史 + 未来7天预测）", color_discrete_map={"历史":"#4facfe","预测":"#f5576c"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(pred, use_container_width=True, hide_index=True)
