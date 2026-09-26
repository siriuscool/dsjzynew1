# -*- coding: utf-8 -*-
"""一键生成学员对人员管理系统全部代码（完整改进版）"""
import os

FILES = {}

# ---------- requirements.txt ----------
FILES["requirements.txt"] = """streamlit
pandas
plotly
scikit-learn
numpy
"""

# ---------- src/__init__.py ----------
FILES["src/__init__.py"] = ""

# ---------- utils/__init__.py ----------
FILES["utils/__init__.py"] = ""

# ---------- src/database.py ----------
FILES["src/database.py"] = '''import sqlite3
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
'''

# ---------- src/init_data.py ----------
FILES["src/init_data.py"] = '''from src.database import get_conn

def init_sample_data():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cadets")
    if c.fetchone()[0] > 0:
        conn.close()
        print("已有数据，跳过")
        return

    platoons = ["一派", "二派", "三派"]
    classes = ["一b","二b","三b","四b","五b","六b","七b","八b","九b"]
    cadets_per_class = 8

    surnames = list("张王李刘陈杨赵孙周吴郑冯蒋沈韩朱秦许何吕施孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝安常乐于时傅齐")
    given_names = list("伟强娜洋静帆磊悦涛敏浩芳明丽勇晨波静鹏敏军磊洋婷鑫宇欣怡哲琪轩然杰琳超雪峰梦刚瑶毅萱健萍俊燕辉红凯霞亮梅斌兰龙竹飞菊鹏荷丹阳青帆蓝文紫武翠斌玉辰蓉泽婉霖瑾豪蕾睿")

    cadet_id = 1

    # 脸部4人
    for role in ["联长", "知道猿", "副联长", "副知道猿"]:
        name = surnames[(cadet_id-1) % len(surnames)] + given_names[(cadet_id-1) % len(given_names)]
        c.execute("INSERT INTO cadets (name,student_id,platoon,class_name,role,phone) VALUES (?,?,?,?,?,?)",
                  (name, f"2024{cadet_id:03d}", "脸部", "脸部", role, f"138{cadet_id:08d}"))
        cadet_id += 1

    # 3个派，每派3个b，每b 8人
    class_idx = 0
    for platoon in platoons:
        # 派长1人
        name = surnames[(cadet_id-1) % len(surnames)] + given_names[(cadet_id-1) % len(given_names)]
        c.execute("INSERT INTO cadets (name,student_id,platoon,class_name,role,phone) VALUES (?,?,?,?,?,?)",
                  (name, f"2024{cadet_id:03d}", platoon, "派长", "派长", f"138{cadet_id:08d}"))
        cadet_id += 1

        for _ in range(3):
            cls = classes[class_idx]
            class_idx += 1
            for i in range(cadets_per_class):
                name = surnames[(cadet_id-1) % len(surnames)] + given_names[(cadet_id-1) % len(given_names)]
                if i == 0: role = "搬涨"
                elif i == 1: role = "副搬涨"
                else: role = "学员"
                c.execute("INSERT INTO cadets (name,student_id,platoon,class_name,role,phone) VALUES (?,?,?,?,?,?)",
                          (name, f"2024{cadet_id:03d}", platoon, cls, role, f"138{cadet_id:08d}"))
                cadet_id += 1

    conn.commit()
    conn.close()
    print(f"已初始化 {cadet_id-1} 名人员（脸部4 + 派长3 + 9个b x 8人）")
'''

# ---------- src/auth.py ----------
FILES["src/auth.py"] = '''import streamlit as st
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
'''

# ---------- src/leave.py ----------
FILES["src/leave.py"] = '''from src.database import get_conn
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
'''

# ---------- src/outing.py ----------
FILES["src/outing.py"] = '''from src.database import get_conn
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
'''

# ---------- src/stay.py ----------
FILES["src/stay.py"] = '''from src.database import get_conn
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
'''

# ---------- src/duty.py ----------
FILES["src/duty.py"] = '''from src.database import get_conn
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
'''

# ---------- src/stats.py ----------
FILES["src/stats.py"] = '''from src.database import get_conn
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
'''

# ---------- src/alert.py ----------
FILES["src/alert.py"] = '''from src.database import get_conn
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
'''

# ---------- src/generate_data.py ----------
FILES["src/generate_data.py"] = '''import csv, random, os
from datetime import datetime, timedelta

def generate_behavior_logs(n=120000, output="data/behavior_logs.csv"):
    os.makedirs("data", exist_ok=True)
    cadet_ids = list(range(1, 80))
    actions = ["请假申请","请假通过","请假驳回","外出登记","归队打卡",
               "留队申请","任务分配","任务完成","超时未归",
               "集合出操","参加训练","集体学习","值班站岗","帮厨",
               "打扫卫生","布置会场"]
    weights = [10,8,3,8,8,6,8,6,2,10,10,8,6,4,5,3]
    locations = ["图书馆","体育馆","超市","医院","邮局","理发店","书店",
                 "会议室","食堂","宿舍楼","训练场","教室"]
    reasons = ["就医","参加考试","参加比赛","家人病重","其他"]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    with open(output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["log_id","cadet_id","action","location","reason","timestamp","duration_hours"])
        for i in range(n):
            rd = random.randint(0, 365)
            rs = random.randint(0, 86400)
            ts = start_date + timedelta(days=rd, seconds=rs)
            action = random.choices(actions, weights=weights)[0]
            w.writerow([i+1, random.choice(cadet_ids), action,
                        random.choice(locations),
                        random.choice(reasons) if "请假" in action else "",
                        ts.strftime("%Y-%m-%d %H:%M:%S"),
                        round(random.uniform(0.5, 72), 1)])
    print(f"已生成 {n} 条行为日志")

if __name__ == "__main__":
    generate_behavior_logs()
'''

# ---------- src/mapreduce_log.py ----------
FILES["src/mapreduce_log.py"] = '''from collections import defaultdict
import csv, time

def mapper(row):
    return (row["action"], 1)

def shuffle(mapped):
    g = defaultdict(list)
    for k, v in mapped:
        g[k].append(v)
    return g

def reducer(grouped):
    return {k: sum(v) for k, v in grouped.items()}

def mapreduce_analyze(path="data/behavior_logs.csv"):
    start = time.time()
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    read_time = time.time() - start

    t1 = time.time()
    mapped = [mapper(r) for r in rows]
    map_time = time.time() - t1

    t2 = time.time()
    grouped = shuffle(mapped)
    shuffle_time = time.time() - t2

    t3 = time.time()
    result = reducer(grouped)
    reduce_time = time.time() - t3

    return {"result": dict(sorted(result.items(), key=lambda x: -x[1])),
            "total_rows": len(rows),
            "read_time": round(read_time,3),
            "map_time": round(map_time,3),
            "shuffle_time": round(shuffle_time,3),
            "reduce_time": round(reduce_time,3),
            "total_time": round(time.time()-start,3)}

if __name__ == "__main__":
    r = mapreduce_analyze()
    print(f"总记录: {r['total_rows']}, 总耗时: {r['total_time']}s")
'''

# ---------- src/spark_analyze.py ----------
FILES["src/spark_analyze.py"] = '''import time

def spark_analyze(path="data/behavior_logs.csv"):
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, hour, to_timestamp
    except ImportError:
        return {"error": "未安装PySpark，请先 pip install pyspark"}

    spark = SparkSession.builder.appName("CadetAnalysis").master("local[*]") \\
        .config("spark.sql.shuffle.partitions", "4").getOrCreate()
    start = time.time()
    df = spark.read.csv(path, header=True, inferSchema=True)
    total = df.count()
    action_dist = df.groupBy("action").count().orderBy(col("count").desc()).toPandas()
    cadet_dist = df.groupBy("cadet_id").count().orderBy(col("count").desc()).toPandas()
    location_dist = df.groupBy("location").count().orderBy(col("count").desc()).toPandas()
    df2 = df.withColumn("ts", to_timestamp("timestamp"))
    hour_dist = df2.withColumn("hour", hour("ts")).groupBy("hour").count().orderBy("hour").toPandas()
    elapsed = time.time() - start
    spark.stop()
    return {"total": total, "action_dist": action_dist, "cadet_dist": cadet_dist,
            "location_dist": location_dist, "hour_dist": hour_dist,
            "elapsed": round(elapsed,3)}

if __name__ == "__main__":
    r = spark_analyze()
    print(r.get("error") or f"总记录: {r['total']}, 耗时: {r['elapsed']}s")
'''

# ---------- src/ml_cluster.py ----------
FILES["src/ml_cluster.py"] = '''import pandas as pd, csv
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def build_cadet_features(path="data/behavior_logs.csv"):
    features = defaultdict(lambda: {"请假次数":0,"外出次数":0,"留队次数":0,
        "任务次数":0,"超时次数":0,"总行为":0,"时长列表":[]})
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cid = row["cadet_id"]; action = row["action"]
            features[cid]["总行为"] += 1
            features[cid]["时长列表"].append(float(row["duration_hours"]))
            if "请假" in action: features[cid]["请假次数"] += 1
            if "外出" in action or "归队" in action: features[cid]["外出次数"] += 1
            if "留队" in action: features[cid]["留队次数"] += 1
            if "任务" in action: features[cid]["任务次数"] += 1
            if "超时" in action: features[cid]["超时次数"] += 1
    rows = []
    for cid, f in features.items():
        rows.append({"cadet_id":cid,"请假次数":f["请假次数"],"外出次数":f["外出次数"],
            "留队次数":f["留队次数"],"任务次数":f["任务次数"],"超时次数":f["超时次数"],
            "平均时长":round(sum(f["时长列表"])/len(f["时长列表"]),2),"总行为":f["总行为"]})
    return pd.DataFrame(rows)

def cluster_cadets(df, n_clusters=3):
    cols = ["请假次数","外出次数","留队次数","任务次数","超时次数"]
    X = StandardScaler().fit_transform(df[cols].values)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df = df.copy()
    df["群体"] = km.fit_predict(X)
    summary = df.groupby("群体")[cols].mean().round(1)
    summary["人数"] = df.groupby("群体").size()
    names = {}
    for idx, row in summary.iterrows():
        if row["超时次数"] > summary["超时次数"].mean() and row["请假次数"] > summary["请假次数"].mean():
            names[idx] = "重点关注型"
        elif row["任务次数"] > summary["任务次数"].mean():
            names[idx] = "积极骨干型"
        else:
            names[idx] = "普通稳定型"
    df["群体名称"] = df["群体"].map(names)
    summary["群体名称"] = summary.index.map(names)
    return df, summary
'''

# ---------- src/predict.py ----------
FILES["src/predict.py"] = '''import pandas as pd, csv
from collections import defaultdict
from sklearn.linear_model import LinearRegression
import numpy as np

def daily_leave_trend(path="data/behavior_logs.csv"):
    daily = defaultdict(int)
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if "请假" in row["action"]:
                daily[row["timestamp"][:10]] += 1
    df = pd.DataFrame(list(daily.items()), columns=["date","count"])
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)

def predict_next_days(df, days=7):
    if len(df) < 3: return None
    df = df.copy(); df["day_index"] = range(len(df))
    X = df[["day_index"]].values; y = df["count"].values
    model = LinearRegression().fit(X, y)
    future_X = np.array([[len(df)+i] for i in range(days)])
    future_y = model.predict(future_X)
    last = df["date"].max()
    future_dates = pd.date_range(last + pd.Timedelta(days=1), periods=days)
    result = pd.DataFrame({"date": future_dates, "预测请假数": np.round(future_y,1)})
    return result, round(model.score(X, y), 3)
'''

# ---------- src/activity_score.py ----------
FILES["src/activity_score.py"] = '''import csv
from collections import defaultdict

def build_activity_features(path="data/behavior_logs.csv"):
    features = defaultdict(lambda: {"任务参与":0,"留队次数":0,"集体活动":0,
        "请假次数":0,"超时次数":0,"归队及时":0,"总行为":0})
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cid = row["cadet_id"]; action = row["action"]
            features[cid]["总行为"] += 1
            if "任务" in action: features[cid]["任务参与"] += 1
            if "留队" in action: features[cid]["留队次数"] += 1
            if any(k in action for k in ["集合","训练","学习","值班","帮厨","打扫","会场"]):
                features[cid]["集体活动"] += 1
            if "请假" in action: features[cid]["请假次数"] += 1
            if "超时" in action: features[cid]["超时次数"] += 1
            if "归队" in action: features[cid]["归队及时"] += 1
    return features

def calc_activity_score(features):
    results = []
    max_duty = max(f["任务参与"] for f in features.values()) or 1
    max_stay = max(f["留队次数"] for f in features.values()) or 1
    max_act = max(f["集体活动"] for f in features.values()) or 1
    max_leave = max(f["请假次数"] for f in features.values()) or 1
    max_over = max(f["超时次数"] for f in features.values()) or 1
    max_ret = max(f["归队及时"] for f in features.values()) or 1
    for cid, f in features.items():
        duty = f["任务参与"]/max_duty*100
        stay = f["留队次数"]/max_stay*100
        act = f["集体活动"]/max_act*100
        ret = f["归队及时"]/max_ret*100
        leave_p = f["请假次数"]/max_leave*100
        over_p = f["超时次数"]/max_over*100
        score = duty*0.30 + act*0.25 + stay*0.15 + ret*0.10 - leave_p*0.12 - over_p*0.08
        score = max(0, min(100, round(score,1)))
        if score >= 85: level = "🌟 积极分子"
        elif score >= 70: level = "✅ 表现良好"
        elif score >= 50: level = "⚠️ 需要关注"
        else: level = "🚨 重点关注"
        results.append({"cadet_id":cid,"积极性得分":score,"等级":level,
            "任务参与":f["任务参与"],"集体活动":f["集体活动"],
            "留队次数":f["留队次数"],"请假次数":f["请假次数"],"超时次数":f["超时次数"]})
    return sorted(results, key=lambda x: -x["积极性得分"])
'''

# ---------- utils/style.py ----------
FILES["utils/style.py"] = '''import streamlit as st

def apply_dark_theme():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg,#0f0c29,#302b63,#24243e); color:#eee; }
    .neon-title { font-size:42px; font-weight:900; text-align:center;
        background: linear-gradient(90deg,#00f2fe,#4facfe,#00f2fe);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        text-shadow:0 0 30px rgba(79,172,254,0.5); letter-spacing:2px; }
    .glass-card { background:rgba(255,255,255,0.08); backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.15); border-radius:18px;
        padding:22px; text-align:center; box-shadow:0 8px 32px rgba(0,0,0,0.3);
        transition:all 0.3s; }
    .glass-card:hover { transform:translateY(-6px); border-color:#4facfe;
        box-shadow:0 12px 40px rgba(79,172,254,0.4); }
    .glass-card .label { font-size:14px; color:#9ab; }
    .glass-card .value { font-size:30px; font-weight:bold;
        background: linear-gradient(90deg,#00f2fe,#4facfe);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    [data-testid="stSidebar"] { background:rgba(15,12,41,0.95);
        border-right:1px solid rgba(79,172,254,0.2); }
    </style>""", unsafe_allow_html=True)

def glass_card(col, label, value, icon=""):
    col.markdown(f"""<div class="glass-card">
        <div class="label">{icon} {label}</div>
        <div class="value">{value}</div></div>""", unsafe_allow_html=True)

def sub_title(text):
    st.markdown(f'<h3 style="color:#4facfe;border-left:4px solid #4facfe;'
                f'padding-left:12px;margin:20px 0 10px 0;">{text}</h3>',
                unsafe_allow_html=True)
'''

# ---------- app.py ----------
FILES["app.py"] = '''import streamlit as st
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
        st.markdown("- 📊 数据看板\\n- 📝 请假管理\\n- 🚪 外出管理\\n- 🏠 留队管理\\n- 🔧 任务管理\\n- 👥 人员管理\\n- ⚡ 大数据分析\\n- 🤖 智能挖掘\\n- 🎯 积极性评价\\n- 📁 数据明细")
    with c2:
        st.markdown("### 🎯 系统特色")
        st.markdown("- ✅ 脸部-派-b三级建制\\n- ✅ 四大业务模块\\n- ✅ 四级权限管理\\n- ✅ MapReduce + PySpark\\n- ✅ KMeans 聚类 + 预测\\n- ✅ 积极性综合评分")
    with c3:
        st.markdown("### 📊 快速统计")
        from src.stats import get_overview
        for k, v in get_overview().items():
            st.metric(k, v)
    if st.button("退出登录"):
        st.session_state.clear()
        st.rerun()
'''

# ---------- pages/1_数据看板.py ----------
FILES["pages/1_📊_数据看板.py"] = '''import streamlit as st
from utils.style import apply_dark_theme, glass_card
from src.auth import check_login, require_level
from src.stats import get_overview, leave_trend, leave_by_reason, platoon_compare, duty_by_task
import plotly.express as px

st.set_page_config(page_title="数据看板", page_icon="📊", layout="wide")
apply_dark_theme()
check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">📊 数据看板</div>', unsafe_allow_html=True)
st.markdown("---")

s = get_overview()
c = st.columns(6)
glass_card(c[0], "总人数", s["总人数"], "👥")
glass_card(c[1], "在队", s["在队"], "✅")
glass_card(c[2], "请假中", s["请假中"], "📝")
glass_card(c[3], "外出中", s["外出中"], "🚪")
glass_card(c[4], "留队", s["留队"], "🏠")
glass_card(c[5], "任务", s["公差"], "🔧")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    df = leave_trend()
    if not df.empty:
        st.plotly_chart(px.line(df, x="date", y="count", markers=True, title="请假趋势"), use_container_width=True)
with col2:
    df = leave_by_reason()
    if not df.empty:
        st.plotly_chart(px.pie(df, names="reason", values="count", hole=0.4, title="请假事由分布"), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    df = platoon_compare()
    if not df.empty:
        st.plotly_chart(px.bar(df, x="platoon", y="请假次数", color="请假次数", color_continuous_scale="Blues", title="各派请假对比"), use_container_width=True)
with col2:
    df = duty_by_task()
    if not df.empty:
        st.plotly_chart(px.bar(df, x="task_name", y="count", color="count", color_continuous_scale="Sunset", title="任务类型分布"), use_container_width=True)
'''

# ---------- pages/2_请假管理.py ----------
FILES["pages/2_📝_请假管理.py"] = '''import streamlit as st
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
'''

# ---------- pages/3_外出管理.py ----------
FILES["pages/3_🚪_外出管理.py"] = '''import streamlit as st
from utils.style import apply_dark_theme
from src.auth import check_login, is_admin
from src.outing import register_outing, mark_return, get_outings, can_go_out

st.set_page_config(page_title="外出管理", page_icon="🚪", layout="wide")
apply_dark_theme()
u = check_login()
st.markdown('<div class="neon-title">🚪 外出管理</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2 = st.tabs(["📋 外出记录", "➕ 外出登记"])
with t1:
    df = get_outings()
    if df.empty: st.info("暂无外出记录")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        if is_admin():
            st.subheader("归队登记")
            for _, r in get_outings(status="外出中").iterrows():
                c1, c2 = st.columns([3,1])
                with c1: st.write(f"**{r['name']}** - {r['destination']}（应归：{r['back_time']}）")
                with c2:
                    if st.button("✅ 已归队", key=f"b{r['id']}"):
                        mark_return(r["id"]); st.rerun()
with t2:
    st.subheader("外出登记")
    st.info("⚠️ 学员两周内只能外出一次")
    if not can_go_out(u["id"]):
        st.error("❌ 两周内已外出过，不能再次外出")
    else:
        dest = st.text_input("外出地点")
        c1, c2 = st.columns(2)
        with c1:
            od = st.date_input("外出日期"); ot = st.time_input("外出时间")
        with c2:
            bd = st.date_input("预计归队日期"); bt = st.time_input("预计归队时间")
        comp = st.text_input("同行人（可选）")
        if st.button("登记外出"):
            register_outing(u["id"], dest, f"{od} {ot}", f"{bd} {bt}", comp)
            st.success("外出登记成功"); st.rerun()
'''

# ---------- pages/4_留队管理.py ----------
FILES["pages/4_🏠_留队管理.py"] = '''import streamlit as st
from utils.style import apply_dark_theme
from src.auth import check_login
from src.stay import apply_stay, get_stays

st.set_page_config(page_title="留队管理", page_icon="🏠", layout="wide")
apply_dark_theme()
u = check_login()
st.markdown('<div class="neon-title">🏠 留队管理</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2 = st.tabs(["📋 留队记录", "➕ 申请留队"])
with t1:
    df = get_stays()
    if df.empty: st.info("暂无留队记录")
    else: st.dataframe(df, use_container_width=True, hide_index=True)
with t2:
    st.subheader("申请留队")
    d = st.date_input("留队日期")
    reason = st.selectbox("留队原因", ["周末留队","节假日留队","值班","其他"])
    act = st.selectbox("留队活动", ["自习","训练","值班","休息"])
    if st.button("提交申请"):
        apply_stay(u["id"], str(d), reason, act)
        st.success("留队申请已提交"); st.rerun()
'''

# ---------- pages/5_任务管理.py ----------
FILES["pages/5_🔧_任务管理.py"] = '''import streamlit as st
from utils.style import apply_dark_theme
from src.auth import check_login, is_admin, require_level
from src.duty import assign_duty, complete_duty, get_duties
from src.database import get_conn
import pandas as pd

st.set_page_config(page_title="任务管理", page_icon="🔧", layout="wide")
apply_dark_theme()
u = check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">🔧 任务管理</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2 = st.tabs(["📋 任务记录", "➕ 分配任务"])
with t1:
    df = get_duties()
    if df.empty: st.info("暂无任务记录")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        if is_admin():
            st.subheader("标记完成")
            for _, r in get_duties(status="待完成").iterrows():
                c1, c2 = st.columns([3,1])
                with c1: st.write(f"**{r['task_name']}** - {r['name']}（{r['location']}）")
                with c2:
                    if st.button("✅ 完成", key=f"d{r['id']}"):
                        complete_duty(r["id"]); st.rerun()
with t2:
    if not is_admin(): st.warning("仅搬涨及以上可分配任务")
    else:
        st.subheader("分配任务")
        tn = st.text_input("任务名称"); loc = st.text_input("地点")
        c1, c2 = st.columns(2)
        with c1: sd = st.date_input("开始日期")
        with c2: ed = st.date_input("结束日期")
        nn = st.number_input("需要人数", 1, 10, 1)
        conn = get_conn()
        cad = pd.read_sql_query("SELECT id,name,platoon,class_name FROM cadets WHERE role='学员'", conn)
        conn.close()
        opts = {f"{r['name']}（{r['platoon']}{r['class_name']}）": r['id'] for _, r in cad.iterrows()}
        sel = st.multiselect("选择人员", list(opts.keys()))
        if st.button("分配任务"):
            if tn and sel:
                for n in sel: assign_duty(tn, loc, str(sd), str(ed), nn, opts[n])
                st.success(f"已分配给 {len(sel)} 人"); st.rerun()
            else: st.warning("请填写完整信息")
'''

# ---------- pages/6_人员管理.py ----------
FILES["pages/6_👥_人员管理.py"] = '''import streamlit as st
from utils.style import apply_dark_theme, sub_title
from src.auth import check_login, require_level
from src.database import get_conn
import pandas as pd

st.set_page_config(page_title="人员管理", page_icon="👥", layout="wide")
apply_dark_theme()
check_login()
require_level(3)  # 派长及以上
st.markdown('<div class="neon-title">👥 人员管理</div>', unsafe_allow_html=True)
st.markdown("---")

conn = get_conn()
df = pd.read_sql_query("SELECT id,name,student_id,platoon,class_name,role,phone,status FROM cadets ORDER BY id", conn)
conn.close()
sub_title(f"全员名单（共 {len(df)} 人）")
sel = st.selectbox("按派筛选", ["全部"] + sorted(df["platoon"].unique().tolist()))
if sel != "全部": df = df[df["platoon"] == sel]
st.dataframe(df, use_container_width=True, hide_index=True)

sub_title("建制分布")
c1, c2 = st.columns(2)
with c1:
    st.dataframe(df.groupby("platoon").size().reset_index(name="人数"), use_container_width=True, hide_index=True)
with c2:
    st.dataframe(df.groupby("role").size().reset_index(name="人数"), use_container_width=True, hide_index=True)
'''

# ---------- pages/7_大数据分析.py ----------
FILES["pages/7_⚡_大数据分析.py"] = '''import streamlit as st
from utils.style import apply_dark_theme, glass_card, sub_title
from src.auth import check_login, require_level
from src.mapreduce_log import mapreduce_analyze
from src.spark_analyze import spark_analyze
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="大数据分析", page_icon="⚡", layout="wide")
apply_dark_theme()
check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">⚡ 大数据分析引擎</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#9ab;">MapReduce 分布式思想 + PySpark 计算</p>', unsafe_allow_html=True)
st.markdown("---")

sub_title("🔷 MapReduce 行为分析")
if st.button("🚀 运行 MapReduce 分析", use_container_width=True):
    with st.spinner("Map → Shuffle → Reduce 执行中..."):
        r = mapreduce_analyze()
    c = st.columns(4)
    glass_card(c[0], "总记录数", f"{r['total_rows']:,}", "📊")
    glass_card(c[1], "Map耗时", f"{r['map_time']}s", "⚙️")
    glass_card(c[2], "Shuffle耗时", f"{r['shuffle_time']}s", "🔀")
    glass_card(c[3], "Reduce耗时", f"{r['reduce_time']}s", "📉")
    st.markdown("---")
    df = pd.DataFrame(list(r["result"].items()), columns=["行为类型","次数"])
    fig = px.bar(df, x="行为类型", y="次数", color="次数", color_continuous_scale="Turbo", text="次数", title="MapReduce 统计结果")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
sub_title("🔶 PySpark 分布式分析")
if st.button("⚡ 运行 PySpark 分析", use_container_width=True):
    with st.spinner("PySpark 运行中..."):
        r = spark_analyze()
    if "error" in r:
        st.warning(r["error"]); st.info("未安装PySpark不影响其他功能。")
    else:
        c = st.columns(2)
        glass_card(c[0], "总记录数", f"{r['total']:,}", "📊")
        glass_card(c[1], "Spark耗时", f"{r['elapsed']}s", "⚡")
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(r["action_dist"], names="action", values="count", hole=0.4, title="行为类型分布"), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(r["location_dist"], x="location", y="count", color="count", color_continuous_scale="Sunset", title="地点分布"), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.bar(r["cadet_dist"], x="cadet_id", y="count", color="count", color_continuous_scale="Blues", title="各学员行为次数"), use_container_width=True)
        with c2:
            st.plotly_chart(px.line(r["hour_dist"], x="hour", y="count", markers=True, title="24小时行为分布"), use_container_width=True)
'''

# ---------- pages/8_智能挖掘.py ----------
FILES["pages/8_🤖_智能挖掘.py"] = '''import streamlit as st
from utils.style import apply_dark_theme, glass_card, sub_title
from src.auth import check_login, require_level
from src.ml_cluster import build_cadet_features, cluster_cadets
from src.predict import daily_leave_trend, predict_next_days
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="智能挖掘", page_icon="🤖", layout="wide")
apply_dark_theme()
check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">🤖 智能数据挖掘</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#9ab;">KMeans 聚类 · 线性回归预测</p>', unsafe_allow_html=True)
st.markdown("---")

sub_title("🔮 学员行为聚类（KMeans）")
if st.button("🎯 运行聚类分析", use_container_width=True):
    with st.spinner("正在聚类..."):
        df = build_cadet_features()
        clustered, summary = cluster_cadets(df, n_clusters=3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(summary.iterrows()):
        glass_card(cols[i], row["群体名称"], f"{int(row['人数'])}人", "👥")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.scatter(clustered, x="请假次数", y="外出次数", color="群体名称", size="总行为", hover_data=["cadet_id"], title="学员群体分布（请假 vs 外出）", color_discrete_sequence=px.colors.qualitative.Set2), use_container_width=True)
    with c2:
        st.plotly_chart(px.scatter(clustered, x="任务次数", y="超时次数", color="群体名称", size="总行为", hover_data=["cadet_id"], title="学员群体分布（任务 vs 超时）", color_discrete_sequence=px.colors.qualitative.Set2), use_container_width=True)
    sub_title("各群体特征对比")
    st.dataframe(summary, use_container_width=True)
    sub_title("学员明细")
    st.dataframe(clustered, use_container_width=True, hide_index=True)

st.markdown("---")
sub_title("📈 请假趋势预测（线性回归）")
if st.button("🔮 预测未来7天请假趋势", use_container_width=True):
    with st.spinner("正在预测..."):
        df = daily_leave_trend()
        result = predict_next_days(df, days=7)
    if result is None: st.warning("数据不足")
    else:
        pred, r2 = result
        c1, c2 = st.columns(2)
        glass_card(c1, "预测天数", "7天", "📅")
        glass_card(c2, "模型拟合度 R²", f"{r2}", "📊")
        st.markdown("---")
        hist = df.tail(30).copy(); hist["类型"] = "历史"
        p = pred.copy(); p.columns = ["date","count"]; p["类型"] = "预测"
        combined = pd.concat([hist, p])
        fig = px.line(combined, x="date", y="count", color="类型", markers=True, title="请假趋势（历史 + 未来7天预测）", color_discrete_map={"历史":"#4facfe","预测":"#f5576c"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(pred, use_container_width=True, hide_index=True)
'''

# ---------- pages/9_积极性评价.py ----------
FILES["pages/9_🎯_积极性评价.py"] = '''import streamlit as st
from utils.style import apply_dark_theme, glass_card, sub_title
from src.auth import check_login, require_level
from src.activity_score import build_activity_features, calc_activity_score
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="积极性评价", page_icon="🎯", layout="wide")
apply_dark_theme()
check_login()
require_level(2)  # 搬涨及以上
st.markdown('<div class="neon-title">🎯 学员积极性综合评价</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#9ab;">基于行为数据的多维度综合评分模型</p>', unsafe_allow_html=True)
st.markdown("---")

@st.cache_data
def load():
    features = build_activity_features()
    return pd.DataFrame(calc_activity_score(features))

df = load()
c = st.columns(4)
glass_card(c[0], "积极分子", len(df[df["等级"]=="🌟 积极分子"]), "🌟")
glass_card(c[1], "表现良好", len(df[df["等级"]=="✅ 表现良好"]), "✅")
glass_card(c[2], "需要关注", len(df[df["等级"]=="⚠️ 需要关注"]), "⚠️")
glass_card(c[3], "重点关注", len(df[df["等级"]=="🚨 重点关注"]), "🚨")
st.markdown("---")

sub_title("🏆 积极性排行榜")
top = df.head(10).copy(); top["学员"] = "学员" + top["cadet_id"].astype(str)
fig = px.bar(top, x="积极性得分", y="学员", orientation="h", color="积极性得分", color_continuous_scale="Turbo", text="积极性得分", title="积极性Top10")
fig.update_traces(textposition="outside")
fig.update_layout(yaxis=dict(autorange="reversed"), height=450)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    lc = df["等级"].value_counts().reset_index(); lc.columns = ["等级","人数"]
    st.plotly_chart(px.pie(lc, names="等级", values="人数", hole=0.45, color_discrete_sequence=["#43e97b","#4facfe","#fa709a","#f5576c"], title="积极性等级分布"), use_container_width=True)
with c2:
    st.plotly_chart(px.scatter(df, x="请假次数", y="任务参与", size="积极性得分", color="等级", hover_data=["cadet_id"], title="请假 vs 任务参与（气泡=得分）", color_discrete_map={"🌟 积极分子":"#43e97b","✅ 表现良好":"#4facfe","⚠️ 需要关注":"#fa709a","🚨 重点关注":"#f5576c"}), use_container_width=True)

st.markdown("---")
sub_title("📋 全部学员评分明细")
st.dataframe(df, use_container_width=True, hide_index=True)
sub_title("🚨 重点关注名单")
d = df[df["等级"]=="🚨 重点关注"]
st.success("暂无重点关注学员") if d.empty else st.dataframe(d, use_container_width=True, hide_index=True)
'''

# ---------- pages/10_数据明细.py ----------
FILES["pages/10_📁_数据明细.py"] = '''import streamlit as st
from utils.style import apply_dark_theme, sub_title
from src.auth import check_login, require_level
from src.database import get_conn
import pandas as pd

st.set_page_config(page_title="数据明细", page_icon="📁", layout="wide")
apply_dark_theme()
check_login()
require_level(3)  # 派长及以上
st.markdown('<div class="neon-title">📁 数据明细</div>', unsafe_allow_html=True)
st.markdown("---")

t1, t2 = st.tabs(["👥 人员数据", "📊 行为日志"])
with t1:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cadets", conn)
    conn.close()
    sub_title(f"人员数据（共 {len(df)} 条）")
    st.dataframe(df, use_container_width=True, hide_index=True)
with t2:
    try:
        df = pd.read_csv("data/behavior_logs.csv", encoding="utf-8-sig")
        sub_title(f"行为日志（共 {len(df):,} 条，显示前1000条）")
        st.dataframe(df.head(1000), use_container_width=True, hide_index=True)
        csv = df.head(1000).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("⬇️ 下载前1000条", csv, "behavior_sample.csv", "text/csv")
    except FileNotFoundError:
        st.warning("行为日志未生成，请先运行 python src/generate_data.py")
'''

# ---------- README.md ----------
FILES["README.md"] = '''# 学员对人员管理系统（大数据版）

## 建制
脸部4人 + 3派长 + 9个b x 8人 = 79人

## 角色
联长 / 知道猿 / 副联长 / 副知道猿 / 派长 / 搬涨 / 副搬涨 / 学员

## 运行
```bash
pip install -r requirements.txt
python src/generate_data.py
python -m streamlit run app.py
'''

def main():
    print("=" * 50)
    print("正在生成学员对人员管理系统全部代码...")
    print("=" * 50)
    for path, content in FILES.items():
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [OK] {path}")
    print("=" * 50)
    print(f"共生成 {len(FILES)} 个文件")
    print("=" * 50)
    print()
    print("接下来执行：")
    print("  1. pip install -r requirements.txt")
    print("  2. python src/generate_data.py")
    print("  3. python -m streamlit run app.py")
    print()
    print("测试账号（密码均 123456）：")
    print("  2024001 联长 | 2024005 派长 | 2024008 搬涨 | 2024016 学员")


if __name__ == "__main__":
    main()