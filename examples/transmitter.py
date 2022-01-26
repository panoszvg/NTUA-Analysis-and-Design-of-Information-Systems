import json
import pika
import socket
import sys
import os

from pika.exceptions import ChannelClosed, StreamLostError

serverSocket = None
conn = None

def callback(ch, method, properties, body):
    body = body.decode('utf8').replace("'", '"') + "\n"
    # Send to client
    global conn
    conn.sendall(body.encode('utf8'))

def create_channel(host, port, user, passw):
    # Create connection with message layer
    creds = pika.PlainCredentials(user, passw)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port, credentials=creds))
    
    return connection.channel()

def start_consume():
    channel = create_channel(HOSTNAME, PORT, USERNAME, PASSWORD)
    channel.basic_consume(
            queue=QUEUE, on_message_callback=callback, auto_ack=True
        )    
    channel.start_consuming()

def start_stream(): 
    # Create server that listens for clients
    global serverSocket
    if serverSocket == None:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((HOSTNAME, QUEUE_PORT))
    serverSocket.listen(1)
    print(f'Waiting for client to connect to {QUEUE}.', flush=True)
    global conn
    conn, addr = serverSocket.accept()
    print(f"Client with {addr} connected.", flush=True)

    # Consume queue until an error occurs
    while True:
        try:
            start_consume()
        except StreamLostError:
            continue

if __name__ == '__main__':
    HOSTNAME = os.environ.get("BROKER_IP")
    PORT = int(os.environ.get("BROKER_PORT"))
    USERNAME = os.environ.get("BROKER_USER")
    PASSWORD = os.environ.get("BROKER_PASSW")

    QUEUE = os.environ.get("QUEUE")
    QUEUE_PORT = int(os.environ.get("QUEUE_PORT"))

    conn = None

    try:
        start_stream()
    except (BrokenPipeError, ChannelClosed):
        print("Exception ChannelClosed: Restarting channel", flush=True)
        conn.close()
        start_stream()
    except KeyboardInterrupt:
        conn.close()