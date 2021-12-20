import json
import time

from rhea import AreaManager, Sender

AREA = "A"
EXCHANGES = ["temperature_sensors"]
QUEUES = ["ontime_temperatures", "late_temperatures"]
BINDING = ["ontime.temp", "late.temp"]
HOSTNAME = "<BROKER_IP>"
PORT = "<BROKER_PORT>"

# Create an area manager - send_interval = 20s, late_pct = 1/30
am = AreaManager(AREA, HOSTNAME, PORT, 20, 1/30)
print(f"Successfully created AreaManager in area {AREA}.")

# Create exchange for the area
for exch in EXCHANGES:
    am.create_exchange(exch, "topic")
    print(f"Successfully created Exchange {exch}.")

# Create queues for the area
for queue in QUEUES:
    am.create_queue(queue)
    print(f"Successfully created Exchange {queue}.")

# Bind queues to exchange
am.bind_queue_to_exchange("temperature_sensors", "ontime_temperatures", "ontime.temp")
print("Successfully binded ontime_temperatures to temperature_sensors (ontime.temp).")
am.bind_queue_to_exchange("temperature_sensors", "late_temperatures", "late.temp")
print("Successfully binded late_temperatures to temperature_sensors (late.temp).")

# Add senders to area
for i in range(2):
    am.add_sender_to_area("temp")
    print(f"Successfully added sender {i} in area A")

# Activate area
print("About to activate area A.")
am.activate_area("temperature_sensors")