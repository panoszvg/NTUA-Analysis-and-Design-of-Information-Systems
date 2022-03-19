import json
import time

from datetime import datetime
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.types import *

# Run this file like this:
# spark-submit --packages org.mongodb.spark:mongo-spark-connector_2.11:2.3.1 mongo_consumer.py

BROKER = "<IP>"
PORT = "<QUEUE_PORT>"

MONGO_URI = "<MOGO_URI>"
COLLECTION = "<COLLECTION_NAME>"

def convertLoad(x):
        x = json.loads(x)

        sender_no = x["sender_no"]
        # Convert time object to iso 8601 string
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z", tuple(x["event_timestamp"]))
        # Convert string to datetime object
        timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
        value = x["value"]

        return ((sender_no, "temperature"), timestamp, value)

def write_to_db(rdd):
        schema = StructType([
                StructField('metadata', StructType([
                        StructField('sender_no', IntegerType(), False),
                        StructField('type', StringType(), False)
                        ])),
                StructField('timestamp', TimestampType(), False),
                StructField('value', DoubleType(), False),
        ])
        val = spark.createDataFrame(rdd, schema)
        val.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").option("collection", COLLECTION).save()

conf = SparkConf()
# Configure master correctlly (sockets + 1)
conf = conf.setMaster("local[2]")
conf = conf.set("spark.mongodb.output.uri", MONGO_URI)

sc = SparkContext(conf=conf)
spark = SparkSession(sc)
ssc = StreamingContext(sc, 90)

mqttStream1 = ssc.socketTextStream(BROKER, PORT)

mqttStreams = [mqttStream1]
mqttStream = ssc.union(*mqttStreams)

values = mqttStream.map(convertLoad)
values.foreachRDD(write_to_db)
values.pprint(20)

ssc.start()
ssc.awaitTermination()