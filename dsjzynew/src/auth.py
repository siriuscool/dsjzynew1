import streamlit as st
from src.database import get_conn

def login(student_id, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,name,role,platoon,class_name FROM cadets WHERE student_id=? AND password=?",
              (student_id, password))
    user = c.fetchone()
    conn.close()
    return user

def register(name, student_id, password, platoon, class_name, phone):
    """注册新学员，默认角色：学员"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM cadets WHERE student_id=?", (student_id,))
    if c.fetchone():
        conn.close()
        return False, "学号已存在"
    c.execute("""INSERT INTO cadets (name, student_id, platoon, class_name, role, password, phone)
                 VALUES (?, ?, ?, ?, '学员', ?, ?)""",
              (name, student_id, platoon, class_name, password, phone))
    conn.commit()
    conn.close()
    return True, "注册成功"

def check_login():
    if "user" not in st.session_state:
        st.warning("请先登录")
        st.stop()
    return st.session_state["user"]

def get_role_level(role):
    levels = {"联长":4, "知道猿":4, "副联长":4, "副知道猿":4,
              "派长":3, "搬涨":2, "副搬涨":2, "学员":1}
    return levels.get(role, 1)

def is_admin():
    role = st.session_state.get("user", {}).get("role", "")
    return get_role_level(role) >= 2

def is_leader():
    role = st.session_state.get("user", {}).get("role", "")
    return get_role_level(role) >= 3

def require_level(min_level):
    """要求最低权限等级，不够就拦截"""
    user = st.session_state.get("user", {})
    role = user.get("role", "")
    if get_role_level(role) < min_level:
        st.error("⛔ 权限不足，仅骨干及以上可访问此页面")
        st.stop()
