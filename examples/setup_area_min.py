import json
import os
import time

from rhea import AreaManager, Sender

if __name__ == '__main__':
    AREA = os.environ.get("AREA")
    HOSTNAME = os.environ.get("BROKER_IP")
    PORT = int(os.environ.get("BROKER_PORT"))
    USERNAME = os.environ.get("BROKER_USER")
    PASSWORD = os.environ.get("BROKER_PASSW")
    SEND_INTERVAL = int(os.environ.get("SEND_INTERVAL"))
    LATE_PCT = float(os.environ.get("LATE_PCT"))

    EXCHANGES = ["all_sensors"]
    QUEUES = ["ontime_temperature", "late_temperature", "ontime_humidity", "late_humidity"]
    BINDINGS = ["ontime.temp", "late.temp", "ontime.hum", "late.hum"]

    # Create an area manager - send_interval = 90s, late_pct = 1/30
    am = AreaManager(AREA, HOSTNAME, PORT, USERNAME, PASSWORD, SEND_INTERVAL, LATE_PCT)
    print(f"Successfully created AreaManager in area {AREA}.", flush=True)

    # Create exchange for the area
    for exch in EXCHANGES:
        am.create_exchange(exch, "topic")
        print(f"Successfully created Exchange {exch}.", flush=True)

    # Create queues for the area
    for queue in QUEUES:
        am.create_queue(queue)
        print(f"Successfully created Exchange {queue}.", flush=True)

    # Bind queues to exchange
    for queue, binding_key in zip(QUEUES, BINDINGS):
        am.bind_queue_to_exchange("all_sensors", queue, binding_key)
        print(f"Successfully binded {queue} to all_sensors ({binding_key}).", flush=True)

    # Add senders to area
    sensor_types = ["temp"]
    for i, sensor_type in enumerate(sensor_types):
        am.add_sender_to_area(sensor_type)
        print(f"Successfully added sender {i} in area {AREA}", flush=True)

    # Activate area
    print(f"About to activate area {AREA}.", flush=True)

    try:
        am.terminate_setup()
        am.activate_area("all_sensors", AREA)
    except Exception as e:
        am.terminate_area()
        print(f"Area {AREA} terminated: {e}", flush=True)