import pika 

class Broker:
    def __init__(self, area):
        # Validate broker attributes
        if area not in ["A", "B", "C", "D"]:
            raise ValueError(
                "Please provide a valid sender area. [A, B, C, D]"
            )
        
        self.area = area
        self.connection = None
        self.channel = None
        self.exchanges = []
        self.queues = []

    def open_connection(self, hostname, port):
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
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=hostname,
                port=port
            )
        )

        # Open channel
        self.channel = self.connection.channel()

    def close_connection(self):
        # Close channel first
        self.channel.close()

        # Close collection
        self.connection.close()

    def create_exchange(self, exchange, exchange_type):
        # Validate arguments
        if not isinstance(exchange, str):
            raise ValueError(
                "Please provide a valid exchange of type str."
            )
        if exchange_type not in ["direct", "fanout", "headers", "topic"]:
            raise ValueError(
                "Please provide a valid exchange type. [direct, fanout, headers, topic]"
            )
        
        # Create exchange
        self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)

        # Add exchange name to broker's exchanges
        self.exchanges.append(exchange)

    def create_queue(self, queue):
        # Validate arguments
        if not isinstance(queue, str):
            raise ValueError(
                "Please provide a valid queue of type str."
            )
        
        # Create queue
        self.channel.queue_declare(queue=queue)

        # Add queue name to broker's queues
        self.queues.append(queue)

    def bind_queue_to_exchange(self, exchange, queue, binding_key):
        # Validate arguments
        if exchange not in self.exchanges:
            raise UserWarning(
                "This exchange is not a member of broker's exchanges."
            )
        if queue not in self.queues:
            raise UserWarning(
                "This queue is not a member of broker's queues."
            )
        if not isinstance(binding_key, str):
            raise ValueError(
                "Please provide a valid binding key of type str."
            )

        self.channel.queue_bind(
            exchange=exchange, queue=queue, routing_key=binding_key
            )
