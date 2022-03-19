import json
import os
import time

from datetime import datetime, timezone
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.types import *

def deserializeStream(x):
        x = json.loads(x)

        sender_no = int(x["sender_no"])
        value = float(x["value"])

        created_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z", tuple(x["created_timestamp"]))
        created_timestamp = datetime.strptime(created_timestamp, "%Y-%m-%dT%H:%M:%S%z")

        return (sender_no, (value, created_timestamp))

def write_to_db(rdd, sensor_type, aggr_type):
        schema = StructType([
                StructField('metadata', StructType([
                        StructField('sender_no', IntegerType(), False),
                        StructField('type', StringType(), False)
                        ])),
                StructField('timestamp', TimestampType(), False),
                StructField('value', DoubleType(), False),
        ])
        val = spark.createDataFrame(rdd, schema)
        print("-------------------------------------------")
        print(val)
        print("About to submit:", MONGO_URI)
        val.write.format("mongo"). \
            mode("append").option("collection", f"{sensor_type}{aggr_type.capitalize()}").save()
        print("Send to Mongo:", MONGO_URI)
        print("-------------------------------------------")
        print("")

if __name__ == '__main__':
    BROKERS = json.loads(os.environ.get("BROKERS"))
    PORT = int(os.environ.get("PORT"))
    TYPE = os.environ.get("TYPE")
    BATCH_DURATION = int(os.environ.get("BATCH_DURATION"))
    SPARK_MASTER = os.environ.get("SPARK_MASTER")
    DRIVER_HOST = os.environ.get("DRIVER_HOST")
    MONGO_URI = os.environ.get("MONGO_URI")

    conf = SparkConf()
    conf.setAll([
        ('spark.master', SPARK_MASTER),
        ('spark.submit.deployMode', 'client'),
        ("spark.mongodb.output.uri", MONGO_URI),
        ('spark.driver.host', DRIVER_HOST),
        ('spark.cores.max', 6),
        ('spark.executor.memory', '768m'),
        ('spark.app.name', f"ontime-{TYPE}")
    ])

    sc = SparkContext(conf=conf)
    sc.setLogLevel("INFO")
    spark = SparkSession(sc)
    ssc = StreamingContext(sc, BATCH_DURATION)

    # Listen to all streams
    mqttStreams = []
    for b in BROKERS:
        mqttStreams.append(ssc.socketTextStream(b, PORT))

    mqttStream = ssc.union(*mqttStreams)

    # Deserialize streams (sender_no, (value, created_timestamp))
    values = mqttStream.map(deserializeStream)
    # Keep only the values (sender_no, value)
    values = values.map(lambda x: (x[0], x[1][0]))

    # Aggregates
    # Max (sender_no, max)
    valuesMax = values.reduceByKey(max)
    # ((sender_no, type), timestamp, max)
    valuesMax = valuesMax.map(lambda x: ((x[0], TYPE), datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0), x[1]))

    # Min (sender_no, min)
    valuesMin = values.reduceByKey(min)
    # ((sender_no, type), timestamp, min)
    valuesMin = valuesMin.map(lambda x: ((x[0], TYPE), datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0), x[1]))

    # Sum
    # Add a counter (sender_no, (value, 1))
    valuesSumTmp = values.map(lambda x: (x[0], (x[1], 1)))
    # Get (sender_no, (sum_values, cnt))
    valuesSumTmp = valuesSumTmp.reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1]))
    # Get ((sender_no, type), timestamp, sum)
    valuesSum = valuesSumTmp.map(lambda x: ((x[0], TYPE), datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0), x[1][0]))

    # Avg ((sender_no, type), timestamp, avg)
    valuesAvg = valuesSumTmp.map(lambda x: ((x[0], TYPE), datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0), x[1][0] / x[1][1]))


    # For each RDD send to db
    valuesMax.foreachRDD(lambda rdd: write_to_db(rdd, TYPE, "max"))
    valuesMin.foreachRDD(lambda rdd: write_to_db(rdd, TYPE, "min"))
    valuesSum.foreachRDD(lambda rdd: write_to_db(rdd, TYPE, "sum"))
    valuesAvg.foreachRDD(lambda rdd: write_to_db(rdd, TYPE, "avg"))

    # Log results
    #valuesMax.pprint()
    #valuesMin.pprint()
    #valuesSum.pprint()
    #valuesAvg.pprint()

ssc.start()
ssc.awaitTermination()