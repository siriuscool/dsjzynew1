import csv
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
