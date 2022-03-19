import json

from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.streaming import StreamingContext

BROKER = "<IP>"
PORT_1 = "<QUEUE_PORT>"
PORT_2 = "<QUEUE_PORT>"
PORT_3 = "<QUEUE_PORT>"
PORT_4 = "<QUEUE_PORT>"

conf = SparkConf()
# Configure master correctlly (sockets + 1)
conf = conf.setMaster("local[5]")

sc = SparkContext(conf=conf)
spark = SparkSession(sc)
ssc = StreamingContext(sc, 90)

mqttStream1 = ssc.socketTextStream(BROKER, PORT_1)
mqttStream2 = ssc.socketTextStream(BROKER, PORT_2)
mqttStream3 = ssc.socketTextStream(BROKER, PORT_3)
mqttStream4 = ssc.socketTextStream(BROKER, PORT_4)

mqttStreams = [mqttStream1, mqttStream2, mqttStream3, mqttStream4]
mqttStream = ssc.union(*mqttStreams)

values = mqttStream.map(lambda x: (json.loads(x)["value"], json.loads(x)["sender_no"], json.loads(x)["created_timestamp"], json.loads(x)["event_timestamp"]))
values.pprint(20)

ssc.start()
ssc.awaitTermination()