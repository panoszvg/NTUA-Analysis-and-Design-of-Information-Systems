import json
import os
import subprocess
import time

queues = json.loads(os.environ.get("QUEUES"))
queue_ports = json.loads(os.environ.get("QUEUE_PORTS"))

procs = []

for q, p in zip(queues, queue_ports):
    os.environ["QUEUE"] = q
    os.environ["QUEUE_PORT"] = p
    print(f"Open transmitter for {q} in port {p}", flush=True)
    proc = subprocess.Popen(["python3", "transmitter.py"])
    procs.append(proc)
    time.sleep(1)

exit_codes = [p.wait() for p in procs]