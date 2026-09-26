import csv, random, os
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
