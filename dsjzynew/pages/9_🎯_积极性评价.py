import streamlit as st
from utils.style import apply_dark_theme, glass_card, sub_title
from src.auth import check_login, require_level
from src.activity_score import build_activity_features, calc_activity_score
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="积极性评价", page_icon="🎯", layout="wide")
apply_dark_theme()
check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">🎯 学员积极性综合评价</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#9ab;">基于行为数据的多维度综合评分模型</p>', unsafe_allow_html=True)
st.markdown("---")

@st.cache_data
def load():
    features = build_activity_features()
    return pd.DataFrame(calc_activity_score(features))

df = load()
c = st.columns(4)
glass_card(c[0], "积极分子", len(df[df["等级"]=="🌟 积极分子"]), "🌟")
glass_card(c[1], "表现良好", len(df[df["等级"]=="✅ 表现良好"]), "✅")
glass_card(c[2], "需要关注", len(df[df["等级"]=="⚠️ 需要关注"]), "⚠️")
glass_card(c[3], "重点关注", len(df[df["等级"]=="🚨 重点关注"]), "🚨")
st.markdown("---")

sub_title("🏆 积极性排行榜")
top = df.head(10).copy(); top["学员"] = "学员" + top["cadet_id"].astype(str)
fig = px.bar(top, x="积极性得分", y="学员", orientation="h", color="积极性得分", color_continuous_scale="Turbo", text="积极性得分", title="积极性Top10")
fig.update_traces(textposition="outside")
fig.update_layout(yaxis=dict(autorange="reversed"), height=450)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    lc = df["等级"].value_counts().reset_index(); lc.columns = ["等级","人数"]
    st.plotly_chart(px.pie(lc, names="等级", values="人数", hole=0.45, color_discrete_sequence=["#43e97b","#4facfe","#fa709a","#f5576c"], title="积极性等级分布"), use_container_width=True)
with c2:
    st.plotly_chart(px.scatter(df, x="请假次数", y="任务参与", size="积极性得分", color="等级", hover_data=["cadet_id"], title="请假 vs 任务参与（气泡=得分）", color_discrete_map={"🌟 积极分子":"#43e97b","✅ 表现良好":"#4facfe","⚠️ 需要关注":"#fa709a","🚨 重点关注":"#f5576c"}), use_container_width=True)

st.markdown("---")
sub_title("📋 全部学员评分明细")
st.dataframe(df, use_container_width=True, hide_index=True)
sub_title("🚨 重点关注名单")
d = df[df["等级"]=="🚨 重点关注"]
st.success("暂无重点关注学员") if d.empty else st.dataframe(d, use_container_width=True, hide_index=True)
