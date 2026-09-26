from src.database import get_conn
from datetime import datetime
import pandas as pd

def check_overdue_outings():
    conn = get_conn()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    df = pd.read_sql_query("""SELECT o.id,c.name,c.platoon,c.class_name,o.destination,o.back_time
        FROM outings o JOIN cadets c ON o.cadet_id=c.id
        WHERE o.status='外出中' AND o.back_time<?""", conn, params=[now])
    conn.close()
    return df

def check_frequent_leave(threshold=3):
    conn = get_conn()
    df = pd.read_sql_query("""SELECT c.name,c.platoon,c.class_name,COUNT(*) as leave_count
        FROM leaves l JOIN cadets c ON l.cadet_id=c.id
        WHERE l.status='已通过' GROUP BY c.id
        HAVING leave_count>=? ORDER BY leave_count DESC""", conn, params=[threshold])
    conn.close()
    return df
