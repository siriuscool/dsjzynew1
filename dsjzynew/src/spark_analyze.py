import time

def spark_analyze(path="data/behavior_logs.csv"):
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, hour, to_timestamp
    except ImportError:
        return {"error": "未安装PySpark，请先 pip install pyspark"}

    spark = SparkSession.builder.appName("CadetAnalysis").master("local[*]") \
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
