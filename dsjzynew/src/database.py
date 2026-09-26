import sqlite3
import os

DB_PATH = "data/cadet.db"

def get_conn():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS cadets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_id TEXT UNIQUE NOT NULL,
        platoon TEXT,
        class_name TEXT,
        role TEXT DEFAULT '学员',
        password TEXT DEFAULT '123456',
        phone TEXT,
        status TEXT DEFAULT '在队')""")
    c.execute("""CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cadet_id INTEGER, reason TEXT,
        start_time TEXT, end_time TEXT, destination TEXT,
        status TEXT DEFAULT '待审批', approver TEXT,
        apply_time TEXT, remark TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS outings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cadet_id INTEGER, destination TEXT,
        out_time TEXT, back_time TEXT, actual_back TEXT,
        companion TEXT, status TEXT DEFAULT '外出中', remark TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS stays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cadet_id INTEGER, date TEXT, reason TEXT,
        activity TEXT, status TEXT DEFAULT '已批准', remark TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS duties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT, location TEXT,
        start_time TEXT, end_time TEXT,
        need_num INTEGER, cadet_id INTEGER,
        status TEXT DEFAULT '待完成', remark TEXT)""")
    conn.commit()
    conn.close()
    print("数据库初始化完成")
