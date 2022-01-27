import json
import pika
import socket
import sys
import os

from pika.exceptions import ChannelClosed, StreamLostError

serverSocket = None
serverConn = None

brokerConn = None
brokerChannel = None
consumerTag = None

# Use callback to send consumed message to the connected client
def callback(ch, method, properties, body):
    global serverConn

    body = body.decode('utf8').replace("'", '"') + "\n"
    # Send to client
    serverConn.sendall(body.encode('utf8'))


def start_broker_conn():
    global brokerConn

    # Create connection with message layer
    creds = pika.PlainCredentials(USERNAME, PASSWORD)
    brokerConn = pika.BlockingConnection(
        pika.ConnectionParameters(host=HOSTNAME, port=PORT, credentials=creds))

def start_consume():
    global brokerConn
    global brokerChannel
    global consumerTag

    brokerChannel = brokerConn.channel()
    consumerTag = brokerChannel.basic_consume(
        queue=QUEUE, on_message_callback=callback, auto_ack=True)  
    brokerChannel.start_consuming()

def stop_consume():
    global brokerChannel
    global consumerTag
    #Close brokerChannel
    brokerChannel.basic_cancel(consumerTag)
    brokerChannel.stop_consuming()
    brokerChannel.close()

def start_stream(): 
    # Create server that listens for clients if not already up
    global serverSocket
    if serverSocket == None:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((HOSTNAME, QUEUE_PORT))
    serverSocket.listen(0)
    
    # Wait for a new client to connect
    print(f'Waiting for client to connect to {QUEUE}.', flush=True)
    global serverConn
    serverConn, addr = serverSocket.accept()
    print(f"Client with {addr} connected.", flush=True)

    while True:
        try:
            # Create new connection with broker
            start_broker_conn()

            # Create new channel and start consuming
            start_consume()
        except StreamLostError as e:
            print(e, flush=True)

            stop_consume()
            brokerConn.close()

            continue

if __name__ == '__main__':
    HOSTNAME = os.environ.get("BROKER_IP")
    PORT = int(os.environ.get("BROKER_PORT"))
    USERNAME = os.environ.get("BROKER_USER")
    PASSWORD = os.environ.get("BROKER_PASSW")

    QUEUE = os.environ.get("QUEUE")
    QUEUE_PORT = int(os.environ.get("QUEUE_PORT"))

    try:
        start_stream()
    except (BrokenPipeError, ChannelClosed, socket.error) as e:
        print(e, flush=True)
        print("Restarting process", flush=True)

        # Close connected client
        serverConn.close()

        #Close brokerChannel
        stop_consume()

        #Close brokerConn
        brokerConn.close()

        # Restart server
        start_stream()

    except KeyboardInterrupt:
        serverConn.close()
        serverSocket.close()
        stop_consume()
        brokerConn.close()