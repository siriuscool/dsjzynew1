import pandas as pd, csv
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
