import streamlit as st
from utils.style import apply_dark_theme, glass_card
from src.database import init_db
from src.init_data import init_sample_data
from src.auth import login, register
import plotly.io as pio

st.set_page_config(page_title="学员对人员管理系统", page_icon="🎖️", layout="wide")
apply_dark_theme()
pio.templates["dark_neon"] = pio.templates["plotly_dark"]
pio.templates["dark_neon"].layout.update(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#eee"),
    colorway=["#00f2fe","#4facfe","#f093fb","#f5576c","#43e97b","#fa709a"])
pio.templates.default = "dark_neon"

init_db()
init_sample_data()

st.markdown('<div class="neon-title">🎖️ 学员对人员管理系统</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#9ab;">请假 · 外出 · 留队 · 任务 一体化管理平台</p>', unsafe_allow_html=True)
st.markdown("---")

if "user" not in st.session_state:
    tab1, tab2 = st.tabs(["🔐 登录", "📝 注册"])

    with tab1:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            sid = st.text_input("学号", placeholder="如：2024001", key="login_sid")
            pwd = st.text_input("密码", type="password", placeholder="默认：123456", key="login_pwd")
            if st.button("登录", use_container_width=True, key="login_btn"):
                u = login(sid, pwd)
                if u:
                    st.session_state["user"] = {"id":u[0],"name":u[1],"role":u[2],
                                                "platoon":u[3],"class_name":u[4]}
                    st.success(f"欢迎，{u[1]}（{u[2]}）")
                    st.rerun()
                else:
                    st.error("学号或密码错误")
            st.info("测试账号（密码均123456）：2024001联长 / 2024005派长 / 2024008搬涨 / 2024016学员")

    with tab2:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            r_name = st.text_input("姓名", key="reg_name")
            r_sid = st.text_input("学号", key="reg_sid")
            r_pwd = st.text_input("密码", type="password", key="reg_pwd")
            r_pwd2 = st.text_input("确认密码", type="password", key="reg_pwd2")
            r_platoon = st.selectbox("所属派", ["一派", "二派", "三派"], key="reg_platoon")
            r_class = st.selectbox("所属b", ["一b","二b","三b","四b","五b","六b","七b","八b","九b"], key="reg_class")
            r_phone = st.text_input("手机号", key="reg_phone")
            if st.button("注册", use_container_width=True, key="reg_btn"):
                if not all([r_name, r_sid, r_pwd, r_pwd2]):
                    st.warning("请填写完整")
                elif r_pwd != r_pwd2:
                    st.warning("两次密码不一致")
                else:
                    ok, msg = register(r_name, r_sid, r_pwd, r_platoon, r_class, r_phone)
                    if ok:
                        st.success(msg + "，请返回登录")
                    else:
                        st.error(msg)
else:
    u = st.session_state["user"]
    st.success(f"当前用户：**{u['name']}**（{u['role']}）- {u['platoon']} {u['class_name']}")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📌 功能导航")
        st.markdown("- 📊 数据看板\n- 📝 请假管理\n- 🚪 外出管理\n- 🏠 留队管理\n- 🔧 任务管理\n- 👥 人员管理\n- ⚡ 大数据分析\n- 🤖 智能挖掘\n- 🎯 积极性评价\n- 📁 数据明细")
    with c2:
        st.markdown("### 🎯 系统特色")
        st.markdown("- ✅ 脸部-派-b三级建制\n- ✅ 四大业务模块\n- ✅ 四级权限管理\n- ✅ MapReduce + PySpark\n- ✅ KMeans 聚类 + 预测\n- ✅ 积极性综合评分")
    with c3:
        st.markdown("### 📊 快速统计")
        from src.stats import get_overview
        for k, v in get_overview().items():
            st.metric(k, v)
    if st.button("退出登录"):
        st.session_state.clear()
        st.rerun()
