import pandas as pd, csv
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
