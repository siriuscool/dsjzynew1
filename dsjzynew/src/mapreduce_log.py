from collections import defaultdict
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
