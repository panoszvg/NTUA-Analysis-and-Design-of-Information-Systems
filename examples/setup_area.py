import json
import time
import os
from dotenv import load_dotenv
load_dotenv()

from rhea import AreaManager, Sender

AREA = "A"
EXCHANGES = ["all_sensors"]
QUEUES = ["ontime_temperature", "late_temperature",
          "ontime_humidity", "late_humidity",
          "ontime_ups_battery", "late_ups_battery",
          "ontime_air_quality_index", "late_air_quality_index"]
BINDINGS = ["ontime.temp", "late.temp",
           "ontime.hum", "late.hum",
           "ontime.ups", "late.ups",
           "ontime.aqi", "late.aqi"]

HOSTNAME = os.getenv('BROKER_IP')
PORT = int(os.getenv('BROKER_PORT'))
print(PORT)

# Create an area manager - send_interval = 90s, late_pct = 1/30
am = AreaManager(AREA, HOSTNAME, PORT, 90, 1/30)
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
for queue, binding_key in zip(QUEUES, BINDINGS):
    am.bind_queue_to_exchange("all_sensors", queue, binding_key)
    print(f"Successfully binded {queue} to all_sensors ({binding_key}).")

# Add senders to area
sensor_types = ["temp", "hum", "ups", "aqi"]
for i, sensor_type in enumerate(sensor_types):
    am.add_sender_to_area(sensor_type)
    print(f"Successfully added sender {i} in area A")

# Activate area
print("About to activate area A.")
am.activate_area("all_sensors")