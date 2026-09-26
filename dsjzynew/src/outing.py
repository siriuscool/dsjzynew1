from src.database import get_conn
from datetime import datetime
import pandas as pd

def can_go_out(cadet_id):
    """检查学员两周内是否已外出过"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT COUNT(*) FROM outings
                 WHERE cadet_id=? AND out_time >= date('now', '-14 days')""",
              (cadet_id,))
    count = c.fetchone()[0]
    conn.close()
    return count == 0

def register_outing(cadet_id, destination, out_time, back_time, companion=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO outings (cadet_id,destination,out_time,back_time,companion) VALUES (?,?,?,?,?)",
              (cadet_id, destination, out_time, back_time, companion))
    conn.commit()
    conn.close()

def mark_return(outing_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE outings SET actual_back=?,status='已归队' WHERE id=?",
              (datetime.now().strftime("%Y-%m-%d %H:%M"), outing_id))
    conn.commit()
    conn.close()

def get_outings(status=None):
    conn = get_conn()
    query = """SELECT o.id,c.name,c.platoon,c.class_name,o.destination,
               o.out_time,o.back_time,o.actual_back,o.status,o.companion
               FROM outings o JOIN cadets c ON o.cadet_id=c.id WHERE 1=1"""
    params = []
    if status:
        query += " AND o.status=?"; params.append(status)
    query += " ORDER BY o.out_time DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df
