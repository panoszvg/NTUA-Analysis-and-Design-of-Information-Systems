import json
import numpy as np
import random
import time

from rhea.broker import Broker
from rhea.sender import Sender

class AreaManager:
    def __init__(self, area, hostname, port, username, password, send_interval, late_pct):
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
        self.username = username
        self.password = password
        self.send_interval = send_interval
        self.late_pct = late_pct
        self.broker = Broker(area)
        self.broker.open_connection(self.hostname, self.port, self.username, self.password)
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
        if sensor_type not in ["temp", "hum", "ups", "aqi"]:
            raise ValueError(
                "Please provide a valid sender sensor type. [temp, hum, ups, aqi]"
            )

        # Create sender
        sender = Sender(self.number, self.area, sensor_type)
        self.number = self.number + 1

        # Add sender to manager's senders
        self.senders.append(sender)

    def activate_area(self, exchange, area):
        # Define async intervals not all sender send at the same time
        powers = [2**(i+1) for i in range(len(self.senders)-1)]
        if (sum(powers) == 0):
            async_intervals = [self.send_interval]
        else:
            if round(self.send_interval/sum(powers)) <= 2:
                raise ValueError(
                    """Please provide a bigger send_interval when creating the AreaManager or
                    use less sensors in the area"""
                )
            step = random.randrange(1, round(self.send_interval/sum(powers)))
            async_intervals = [step*powers[i] for i in range(len(self.senders)-1)]

            #Calculate final sleep time
            sleep_time = self.send_interval - sum(async_intervals)
            async_intervals.append(sleep_time)

        out_of_order_time = time.localtime()
        while True:
            late = random.choices([True, False], weights=[self.late_pct, 1-self.late_pct], k=1)[0]

            if late:
                i = 0
                for s in self.senders:
                    time_now = time.localtime()
                    message_dict = {
                        "sender_no": s.number,
                        "area": area,
                        "value": self.create_value(s.get_type()),
                        "created_timestamp": out_of_order_time,
                        "event_timestamp": time_now
                    }
                    message = json.dumps(message_dict)

                    s.open_connection(self.hostname, self.port, self.username, self.password)
                    c = s.create_channel(exchange, "topic")
                    s.send_message(c, exchange, f"late.{s.get_type()}", message)
                    s.close_connection()

                    time.sleep(async_intervals[i])
                    i = i + 1
                out_of_order_time = time.localtime()
            else:
                i = 0
                for s in self.senders:
                    time_now = time.localtime()
                    message_dict = {
                        "sender_no": s.number,
                        "area": area,
                        "value": self.create_value(s.get_type()),
                        "created_timestamp": time_now,
                        "event_timestamp": time_now
                    }
                    message = json.dumps(message_dict)
                    
                    s.open_connection(self.hostname, self.port, self.username, self.password)
                    c = s.create_channel(exchange, "topic")
                    s.send_message(c, exchange, f"ontime.{s.get_type()}", message)
                    s.close_connection()

                    time.sleep(async_intervals[i])
                    i = i + 1

    def terminate_setup(self):
        self.broker.close_connection()

    def terminate_area(self):
        # Terminate senders
        for s in self.senders:
            s.close_connection()

        # Terminate broker
        self.broker.close_connection()

    def create_value(self, sensor_type):
        if sensor_type == "temp":
            # Get random value between 18.3 - 29.4
            return round(np.random.normal(23.85, 5.55), 2)
        elif sensor_type == "hum":
            # Get random value between 0.37 - 0.62
            return np.random.normal(49.5, 12.5) / 100
        elif sensor_type == "ups":
            # Get random value between 0.82 - 1.0
            ups_batt = np.random.normal(91, 9) / 100
            if ups_batt > 1.0:
                ups_batt = 1.0
            return ups_batt
        elif sensor_type == "aqi":
            # Get random value between 0 - 115
            return np.random.poisson(25)
