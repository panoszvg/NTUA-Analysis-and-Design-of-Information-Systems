import pika
import sys

HOSTNAME = "localhost"
PORT = 4000

queue_name=input("Name of queue to consume:")

# Create connection with message layer
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=HOSTNAME, port=PORT))

# Create channel
channel = connection.channel()

print(f' [*] Waiting for {queue_name} logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


# Consume queue
channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()