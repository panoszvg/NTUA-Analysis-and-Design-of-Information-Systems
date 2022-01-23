import pika

class Sender:
    def __init__(self, number, area, sensor_type):
        # Validate sender attributes
        if not isinstance(number, int):
            raise ValueError(
                "Please provide a sender number of type int."
            )
        if area not in ["A", "B", "C", "D"]:
            raise ValueError(
                "Please provide a valid sender area. [A, B, C, D]"
            )
        if sensor_type not in ["temp", "hum", "ups", "aqi"]:
            raise ValueError(
                "Please provide a valid sender sensor type. [temp, hum, ups, aqi]"
            )

        self.number = number
        self.area = area
        self.sensor_type = sensor_type
        self.connection = None
        self.channels = []

    def get_type(self):
        return self.sensor_type

    def open_connection(self, hostname, port, username, password):
        """
        Open connection with the RabbitMQ server
        """
        # Validate arguments
        if not isinstance(hostname, str):
            raise ValueError(
                "Please provide a valid hostname of type str."
            )
        if not isinstance(port, int) or port < 0 or port > 65535:
            raise ValueError(
                "Please provide a valid port of type int. [0-65535]"
            )

        # Open connection
        credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=hostname,
                port=port,
                credentials=credentials
            )
        )

    def close_connection(self):
        # Close all channels first
        for channel in self.channels:
            channel.close()

        # Close connection
        self.connection.close()

    def create_channel(self, exchange, exchange_type):
        # Validate arguments
        if not isinstance(exchange, str):
            raise ValueError(
                "Please provide a valid exchange of type str."
            )
        if exchange_type not in ["direct", "fanout", "headers", "topic"]:
            raise ValueError(
                "Please provide a valid exchange type. [direct, fanout, headers, topic]"
            )

        # Create new channel
        channel = self.connection.channel()

        # Add it to sender channels
        self.channels.append(channel)

        # Verify that exchange exists and is of the correct type
        channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, passive=True)

        return channel

    def send_message(self, channel, exchange, routing_key, message):
        # Validate arguments
        if channel not in self.channels:
            raise UserWarning(
                "This channel is not a member of sender's channels."
            )
        if not isinstance(exchange, str):
            raise ValueError(
                "Please provide a valid exchange of type str."
            )
        if not isinstance(routing_key, str):
            raise ValueError(
                "Please provide a valid routing_key of type str."
            )
        if not isinstance(message, str):
            raise ValueError(
                "Please provide a valid message of type str."
            )
        
        # Send message
        channel.basic_publish(
            exchange=exchange, routing_key=routing_key, body=message
        )
