import streamlit as st
from utils.style import apply_dark_theme, sub_title
from src.auth import check_login, require_level
from src.database import get_conn
import pandas as pd

st.set_page_config(page_title="数据明细", page_icon="📁", layout="wide")
apply_dark_theme()
check_login()
require_level(3)  # 派长及以上
st.markdown('<div class="neon-title">📁 数据明细</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2 = st.tabs(["👥 人员数据", "📊 行为日志"])
with t1:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cadets", conn)
    conn.close()
    sub_title(f"人员数据（共 {len(df)} 条）")
    st.dataframe(df, use_container_width=True, hide_index=True)
with t2:
    try:
        df = pd.read_csv("data/behavior_logs.csv", encoding="utf-8-sig")
        sub_title(f"行为日志（共 {len(df):,} 条，显示前1000条）")
        st.dataframe(df.head(1000), use_container_width=True, hide_index=True)
        csv = df.head(1000).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇️ 下载前1000条", csv, "behavior_sample.csv", "text/csv")
    except FileNotFoundError:
        st.warning("行为日志未生成，请先运行 python src/generate_data.py")
