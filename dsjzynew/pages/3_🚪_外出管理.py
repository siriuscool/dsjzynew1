import streamlit as st
from utils.style import apply_dark_theme
from src.auth import check_login, is_admin
from src.outing import register_outing, mark_return, get_outings, can_go_out

st.set_page_config(page_title="外出管理", page_icon="🚪", layout="wide")
apply_dark_theme()
u = check_login()
st.markdown('<div class="neon-title">🚪 外出管理</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2 = st.tabs(["📋 外出记录", "➕ 外出登记"])
with t1:
    df = get_outings()
    if df.empty: st.info("暂无外出记录")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        if is_admin():
            st.subheader("归队登记")
            for _, r in get_outings(status="外出中").iterrows():
                c1, c2 = st.columns([3,1])
                with c1: st.write(f"**{r['name']}** - {r['destination']}（应归：{r['back_time']}）")
                with c2:
                    if st.button("✅ 已归队", key=f"b{r['id']}"):
                        mark_return(r["id"]); st.rerun()
with t2:
    st.subheader("外出登记")
    st.info("⚠️ 学员两周内只能外出一次")
    if not can_go_out(u["id"]):
        st.error("❌ 两周内已外出过，不能再次外出")
    else:
        dest = st.text_input("外出地点")
        c1, c2 = st.columns(2)
        with c1:
            od = st.date_input("外出日期"); ot = st.time_input("外出时间")
        with c2:
            bd = st.date_input("预计归队日期"); bt = st.time_input("预计归队时间")
        comp = st.text_input("同行人（可选）")
        if st.button("登记外出"):
            register_outing(u["id"], dest, f"{od} {ot}", f"{bd} {bt}", comp)
            st.success("外出登记成功"); st.rerun()
