import json
import pika
import socket
import sys
import os

from pika.exceptions import ChannelClosed

def callback(ch, method, properties, body):
    body = body.decode('utf8').replace("'", '"') + "\n"
    # Send to client
    conn.sendall(body.encode('utf8'))

def start_channel():
    # Create channel
    channel = connection.channel()

    # Create server that listens for clients
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((HOSTNAME, QUEUE_PORT))
    serverSocket.listen(1)
    print(f'Waiting for client to connect to {QUEUE}.')

    conn, addr = serverSocket.accept()
    print(f"Client with {addr} connected.")

    # Consume queue
    channel.basic_consume(
        queue=QUEUE, on_message_callback=callback, auto_ack=True
    )
    
    channel.start_consuming()

if __name__ == '__main__':
    HOSTNAME = os.environ.get("BROKER_IP")
    PORT = int(os.environ.get("BROKER_PORT"))
    USERNAME = os.environ.get("BROKER_USER")
    PASSWORD = os.environ.get("BROKER_PASSW")

    QUEUE = os.environ.get("QUEUE")
    QUEUE_PORT = int(os.environ.get("QUEUE_PORT"))

    conn = None

    # Create connection with message layer
    creds = pika.PlainCredentials(USERNAME, PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=HOSTNAME, port=PORT, credentials=creds))

    try:
        start_channel()
    except ChannelClosed:
        print("Exception ChannelClosed: Restarting channel")
        conn.close()
        start_channel()
    except KeyboardInterrupt:
        conn.close()