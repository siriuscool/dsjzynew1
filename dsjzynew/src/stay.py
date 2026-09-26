from src.database import get_conn
import pandas as pd

def apply_stay(cadet_id, date, reason, activity):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO stays (cadet_id,date,reason,activity) VALUES (?,?,?,?)",
              (cadet_id, date, reason, activity))
    conn.commit()
    conn.close()

def get_stays(date=None):
    conn = get_conn()
    query = """SELECT s.id,c.name,c.platoon,c.class_name,s.date,
               s.reason,s.activity,s.status
               FROM stays s JOIN cadets c ON s.cadet_id=c.id WHERE 1=1"""
    params = []
    if date:
        query += " AND s.date=?"; params.append(date)
    query += " ORDER BY s.date DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df
