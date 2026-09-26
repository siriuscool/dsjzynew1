from src.database import get_conn
from datetime import datetime
import pandas as pd

LEAVE_REASONS = ["就医", "参加考试", "参加比赛", "家人病重", "其他"]
LEAVE_DESTINATIONS = ["医院", "市内", "学校", "家中（仅家人病重）"]

def apply_leave(cadet_id, reason, start, end, destination):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO leaves (cadet_id,reason,start_time,end_time,destination,apply_time) VALUES (?,?,?,?,?,?)",
              (cadet_id, reason, start, end, destination, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def approve_leave(leave_id, status, approver, remark=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE leaves SET status=?,approver=?,remark=? WHERE id=?", (status, approver, remark, leave_id))
    conn.commit()
    conn.close()

def get_leaves(cadet_id=None, status=None):
    conn = get_conn()
    query = """SELECT l.id,c.name,c.platoon,c.class_name,l.reason,
               l.start_time,l.end_time,l.destination,l.status,
               l.approver,l.apply_time,l.remark
               FROM leaves l JOIN cadets c ON l.cadet_id=c.id WHERE 1=1"""
    params = []
    if cadet_id:
        query += " AND l.cadet_id=?"; params.append(cadet_id)
    if status:
        query += " AND l.status=?"; params.append(status)
    query += " ORDER BY l.apply_time DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df
