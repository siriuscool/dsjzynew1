import streamlit as st
from utils.style import apply_dark_theme
from src.auth import check_login, is_admin, require_level
from src.duty import assign_duty, complete_duty, get_duties
from src.database import get_conn
import pandas as pd

st.set_page_config(page_title="任务管理", page_icon="🔧", layout="wide")
apply_dark_theme()
u = check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">🔧 任务管理</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2 = st.tabs(["📋 任务记录", "➕ 分配任务"])
with t1:
    df = get_duties()
    if df.empty: st.info("暂无任务记录")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        if is_admin():
            st.subheader("标记完成")
            for _, r in get_duties(status="待完成").iterrows():
                c1, c2 = st.columns([3,1])
                with c1: st.write(f"**{r['task_name']}** - {r['name']}（{r['location']}）")
                with c2:
                    if st.button("✅ 完成", key=f"d{r['id']}"):
                        complete_duty(r["id"]); st.rerun()
with t2:
    if not is_admin(): st.warning("仅搬涨及以上可分配任务")
    else:
        st.subheader("分配任务")
        tn = st.text_input("任务名称"); loc = st.text_input("地点")
        c1, c2 = st.columns(2)
        with c1: sd = st.date_input("开始日期")
        with c2: ed = st.date_input("结束日期")
        nn = st.number_input("需要人数", 1, 10, 1)
        conn = get_conn()
        cad = pd.read_sql_query("SELECT id,name,platoon,class_name FROM cadets WHERE role='学员'", conn)
        conn.close()
        opts = {f"{r['name']}（{r['platoon']}{r['class_name']}）": r['id'] for _, r in cad.iterrows()}
        sel = st.multiselect("选择人员", list(opts.keys()))
        if st.button("分配任务"):
            if tn and sel:
                for n in sel: assign_duty(tn, loc, str(sd), str(ed), nn, opts[n])
                st.success(f"已分配给 {len(sel)} 人"); st.rerun()
            else: st.warning("请填写完整信息")
