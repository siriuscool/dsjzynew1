import streamlit as st
from utils.style import apply_dark_theme
from src.auth import check_login, is_admin
from src.leave import apply_leave, approve_leave, get_leaves, LEAVE_REASONS, LEAVE_DESTINATIONS

st.set_page_config(page_title="请假管理", page_icon="📝", layout="wide")
apply_dark_theme()
u = check_login()
st.markdown('<div class="neon-title">📝 请假管理</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2, t3 = st.tabs(["📋 请假记录", "➕ 申请请假", "✅ 审批管理"])
with t1:
    df = get_leaves() if is_admin() else get_leaves(cadet_id=u["id"])
    if df.empty: st.info("暂无请假记录")
    else: st.dataframe(df, use_container_width=True, hide_index=True)
with t2:
    st.subheader("提交请假申请")
    reason = st.selectbox("请假事由", LEAVE_REASONS)
    c1, c2 = st.columns(2)
    with c1:
        sd = st.date_input("开始日期"); stt = st.time_input("开始时间")
    with c2:
        ed = st.date_input("结束日期"); et = st.time_input("结束时间")
    dest = st.selectbox("去向", LEAVE_DESTINATIONS)
    if st.button("提交申请"):
        apply_leave(u["id"], reason, f"{sd} {stt}", f"{ed} {et}", dest)
        st.success("申请已提交"); st.rerun()
with t3:
    if not is_admin(): st.warning("仅搬涨及以上可审批")
    else:
        df = get_leaves(status="待审批")
        if df.empty: st.info("暂无待审批记录")
        else:
            for _, r in df.iterrows():
                with st.expander(f"{r['name']} - {r['reason']} ({r['apply_time']})"):
                    st.write(f"**建制**：{r['platoon']} {r['class_name']}")
                    st.write(f"**时间**：{r['start_time']} ~ {r['end_time']}")
                    st.write(f"**去向**：{r['destination']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ 通过", key=f"p{r['id']}"):
                            approve_leave(r["id"], "已通过", u["name"]); st.rerun()
                    with c2:
                        if st.button("❌ 驳回", key=f"r{r['id']}"):
                            approve_leave(r["id"], "已驳回", u["name"]); st.rerun()
