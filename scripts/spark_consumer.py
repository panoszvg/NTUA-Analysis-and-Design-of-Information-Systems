import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

BROKER = "<IP>"
PORT = "<QUEUE_PORT>"

sc = SparkContext()
ssc = StreamingContext(sc, 30)

# Print out the sensor values received
mqttStream = ssc.socketTextStream(BROKER, PORT)
values = mqttStream.map(lambda x: json.loads(x)["value"])
values.pprint()

ssc.start()
ssc.awaitTermination()