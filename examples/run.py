import json
import os
import subprocess
import time

queues = json.loads(os.environ.get("QUEUES"))
queue_ports = json.loads(os.environ.get("QUEUE_PORTS"))

for q, p in zip(queues, queue_ports):
    os.environ["QUEUE"] = q
    os.environ["QUEUE_PORT"] = p
    print(f"Open transmitter for {q} in port {p}", flush=True)
    subprocess.Popen(["python3", "transmitter.py"])
    time.sleep(1)