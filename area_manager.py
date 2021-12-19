import json
import random
import time

from broker import Broker
from sender import Sender

class AreaManager:
    def __init__(self, area, hostname, port, send_interval, late_pct):
        # Validate manager attributes
        if area not in ["A", "B", "C", "D"]:
            raise ValueError(
                "Please provide a valid sender area. [A, B, C, D]"
            )
        if not isinstance(hostname, str):
            raise ValueError(
                "Please provide a valid hostname of type str."
            )
        if not isinstance(port, int) or port < 0 or port > 65535:
            raise ValueError(
                "Please provide a valid port of type int. [0-65535]"
            )
        if not isinstance(send_interval, int) or send_interval < 1:
            raise ValueError(
                "Please provide a valid send_interval (sec) of type int. [1-]"
            )
        if not isinstance(late_pct, float) or late_pct < 0 or late_pct > 1:
            raise ValueError(
                "Please provide a valid late_pct of type float. [0-1]"
            )

        self.area = area
        self.hostname = hostname
        self.port = port
        self.send_interval = send_interval
        self.late_pct = late_pct
        self.broker = Broker(area)
        self.broker.open_connection(self.hostname, self.port)
        self.senders = []
        self.number = 0

    def create_exchange(self, exchange, exchange_type):
        self.broker.create_exchange(exchange, exchange_type)
    
    def create_queue(self, queue):
        self.broker.create_queue(queue)

    def bind_queue_to_exchange(self, exchange, queue, binding_key):
        self.broker.bind_queue_to_exchange(exchange, queue, binding_key)

    def add_sender_to_area(self, sensor_type):
        # Validate arguments
        if sensor_type not in ["temp", "power"]:
            raise ValueError(
                "Please provide a valid sender sensor type. [temp, power]"
            )

        # Create sender
        sender = Sender(self.number, self.area, sensor_type)
        self.number = self.number + 1

        # Add sender to manager's senders
        self.senders.append(sender)

    def activate_area(self, exchange):
        # TODO: Support multiple sensor types. Currently only temp messages are sent

        # Define async intervals not all sender send at the same time
        powers = [2**(i+1) for i in range(len(self.senders))]
        if round(self.send_interval/sum(powers)) <= 2:
            raise ValueError(
                """Please provide a bigger send_interval when creating the AreaManager or
                use less sensors in the area"""
            )
        step = random.randrange(1, round(self.send_interval/sum(powers)))
        async_intervals = [step*powers[i] for i in range(len(self.senders))]

        #Calculate final sleep time
        sleep_time = self.send_interval - sum(async_intervals)
        async_intervals.append(sleep_time)

        # Create channels for senders
        channels = []
        for s in self.senders:
            s.open_connection(self.hostname, self.port)
            c = s.create_channel(exchange, "topic")
            channels.append(c)

        out_of_order_time = time.localtime()
        while True:
            late = random.choices([True, False], weights=[self.late_pct, 1-self.late_pct], k=1)[0]

            if late:
                i = 0
                for s, c in zip(self.senders, channels):
                    time_now = time.localtime()
                    message_dict = {
                        "sender_no": s.number,
                        "value": 20 + random.random() * 5,
                        "created_timestamp": out_of_order_time,
                        "event_timestamp": time_now
                    }
                    message = json.dumps(message_dict)
                    s.send_message(c, exchange, "late.temp", message)
                    time.sleep(async_intervals[i])
                    i = i + 1
                out_of_order_time = time.localtime()
            else:
                i = 0
                for s, c in zip(self.senders, channels):
                    time_now = time.localtime()
                    message_dict = {
                        "sender_no": s.number,
                        "value": 20 + random.random() * 5,
                        "created_timestamp": time_now,
                        "event_timestamp": time_now
                    }
                    message = json.dumps(message_dict)
                    s.send_message(c, exchange, "ontime.temp", message)
                    time.sleep(async_intervals[i])
                    i = i + 1



