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
        area = x["area"]

        created_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z", tuple(x["created_timestamp"]))
        created_timestamp = datetime.strptime(created_timestamp, "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)

        event_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z", tuple(x["event_timestamp"]))
        event_timestamp = datetime.strptime(event_timestamp, "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)

        return (sender_no, area, value, created_timestamp, event_timestamp)

def write_to_db(rdd, sensor_type):
        schema = StructType([
                StructField('sender_no', IntegerType(), False),
                StructField('area', StringType(), False),
                StructField('value', DoubleType(), False),
                StructField('event_timestamp', TimestampType(), False),
                StructField('created_timestamp', TimestampType(), False),
        ])
        val = spark.createDataFrame(rdd, schema)
        print("-------------------------------------------")
        print(val)
        print("About to submit:", MONGO_URI)
        val.write.format("com.mongodb.spark.sql.DefaultSource"). \
            mode("append").option("collection", f"late{sensor_type.capitalize()}").save()
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
        ('spark.app.name', f"late-{TYPE}")
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

    # Deserialize streams (sender_no, area, value, created_timestamp, event_timestamp)
    values = mqttStream.map(deserializeStream)

    # For each RDD send to db
    values.foreachRDD(lambda rdd: write_to_db(rdd, TYPE))

    # Log results
    values.pprint()

ssc.start()
ssc.awaitTermination()