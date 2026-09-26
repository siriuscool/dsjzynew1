from src.database import get_conn
import pandas as pd

def get_overview():
    conn = get_conn()
    s = {}
    s["总人数"] = pd.read_sql_query("SELECT COUNT(*) as n FROM cadets", conn).iloc[0]["n"]
    s["在队"] = pd.read_sql_query("SELECT COUNT(*) as n FROM cadets WHERE status='在队'", conn).iloc[0]["n"]
    s["请假中"] = pd.read_sql_query("SELECT COUNT(*) as n FROM leaves WHERE status='已通过'", conn).iloc[0]["n"]
    s["外出中"] = pd.read_sql_query("SELECT COUNT(*) as n FROM outings WHERE status='外出中'", conn).iloc[0]["n"]
    s["留队"] = pd.read_sql_query("SELECT COUNT(*) as n FROM stays WHERE status='已批准'", conn).iloc[0]["n"]
    s["公差"] = pd.read_sql_query("SELECT COUNT(*) as n FROM duties WHERE status='待完成'", conn).iloc[0]["n"]
    conn.close()
    return s

def leave_trend():
    conn = get_conn()
    df = pd.read_sql_query("SELECT substr(apply_time,1,10) as date,COUNT(*) as count FROM leaves GROUP BY date ORDER BY date", conn)
    conn.close()
    return df

def leave_by_reason():
    conn = get_conn()
    df = pd.read_sql_query("SELECT reason,COUNT(*) as count FROM leaves GROUP BY reason", conn)
    conn.close()
    return df

def leave_by_class():
    conn = get_conn()
    df = pd.read_sql_query("SELECT c.class_name,COUNT(*) as count FROM leaves l JOIN cadets c ON l.cadet_id=c.id GROUP BY c.class_name", conn)
    conn.close()
    return df

def duty_by_task():
    conn = get_conn()
    df = pd.read_sql_query("SELECT task_name,COUNT(*) as count FROM duties GROUP BY task_name", conn)
    conn.close()
    return df

def platoon_compare():
    conn = get_conn()
    df = pd.read_sql_query("""SELECT c.platoon,
        COUNT(DISTINCT c.id) as 人数,
        COUNT(l.id) as 请假次数, COUNT(d.id) as 任务次数
        FROM cadets c
        LEFT JOIN leaves l ON c.id=l.cadet_id
        LEFT JOIN duties d ON c.id=d.cadet_id
        WHERE c.platoon!='脸部' GROUP BY c.platoon""", conn)
    conn.close()
    return df
