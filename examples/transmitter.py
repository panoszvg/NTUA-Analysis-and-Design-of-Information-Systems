import json
import pika
import socket
import sys

HOSTNAME = "<BROKER_IP>"
PORT = "<BROKER_PORT>"

QUEUE="ontime_temperatures"
QUEUE_PORT = "<QUEUE_PORT>"

# Create connection with message layer
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=HOSTNAME, port=PORT))

# Create channel
channel = connection.channel()

# Create server that listens for clients
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((HOSTNAME, QUEUE_PORT))
serverSocket.listen(1)
print(f'Waiting for client to connect to {QUEUE}.')

conn, addr = serverSocket.accept()
print(f"Client with {addr} connected.")

def callback(ch, method, properties, body):
    body = body.decode('utf8').replace("'", '"') + "\n"
    # Send to client
    conn.sendall(body.encode('utf8'))


# Consume queue
channel.basic_consume(
    queue=QUEUE, on_message_callback=callback, auto_ack=True
)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    conn.close()