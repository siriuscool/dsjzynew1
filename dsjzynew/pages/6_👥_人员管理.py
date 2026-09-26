import streamlit as st
from utils.style import apply_dark_theme, sub_title
from src.auth import check_login, require_level
from src.database import get_conn
import pandas as pd

st.set_page_config(page_title="人员管理", page_icon="👥", layout="wide")
apply_dark_theme()
check_login()
require_level(3)  # 派长及以上
st.markdown('<div class="neon-title">👥 人员管理</div>', unsafe_allow_html=True)
st.markdown("---")

conn = get_conn()
df = pd.read_sql_query("SELECT id,name,student_id,platoon,class_name,role,phone,status FROM cadets ORDER BY id", conn)
conn.close()
sub_title(f"全员名单（共 {len(df)} 人）")
sel = st.selectbox("按派筛选", ["全部"] + sorted(df["platoon"].unique().tolist()))
if sel != "全部": df = df[df["platoon"] == sel]
st.dataframe(df, use_container_width=True, hide_index=True)

sub_title("建制分布")
c1, c2 = st.columns(2)
with c1:
    st.dataframe(df.groupby("platoon").size().reset_index(name="人数"), use_container_width=True, hide_index=True)
with c2:
    st.dataframe(df.groupby("role").size().reset_index(name="人数"), use_container_width=True, hide_index=True)
