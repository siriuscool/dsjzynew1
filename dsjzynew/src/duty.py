from src.database import get_conn
import pandas as pd

def assign_duty(task_name, location, start, end, need_num, cadet_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO duties (task_name,location,start_time,end_time,need_num,cadet_id) VALUES (?,?,?,?,?,?)",
              (task_name, location, start, end, need_num, cadet_id))
    conn.commit()
    conn.close()

def complete_duty(duty_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE duties SET status='已完成' WHERE id=?", (duty_id,))
    conn.commit()
    conn.close()

def get_duties(status=None):
    conn = get_conn()
    query = """SELECT d.id,d.task_name,d.location,d.start_time,d.end_time,
               d.need_num,c.name,c.platoon,c.class_name,d.status
               FROM duties d LEFT JOIN cadets c ON d.cadet_id=c.id WHERE 1=1"""
    params = []
    if status:
        query += " AND d.status=?"; params.append(status)
    query += " ORDER BY d.start_time DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df
