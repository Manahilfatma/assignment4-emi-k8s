import urllib.request
import json
import random
import time
import threading
import subprocess
import csv
import os
import sys

URL = "http://emi.local/api/emi"
RESULTS_DIR = "results"

def send_request():
    data = json.dumps({
        "principal": random.randint(100000, 1000000),
        "rate": round(random.uniform(5.0, 15.0), 2),
        "months": random.randint(12, 60)
    }).encode('utf-8')
    req = urllib.request.Request(URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            response.read()
            return True
    except:
        return False

def run_load(rate, duration):
    total = rate * duration
    interval = 1.0 / rate
    start = time.time()
    success = 0
    fail = 0
    
    for i in range(total):
        next_t = start + (i * interval)
        now = time.time()
        if next_t > now:
            time.sleep(next_t - now)
        if send_request():
            success += 1
        else:
            fail += 1
    return success, fail

def get_pod_cpu():
    try:
        output = subprocess.check_output(["kubectl", "top", "pods", "-n", "emi", "--no-headers"]).decode()
        cpu_data = {}
        for line in output.splitlines():
            parts = line.split()
            if "emi-web" in parts[0]:
                cpu_data[parts[0]] = parts[1]
        return cpu_data
    except:
        return {}

def main():
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        
    replicas = sys.argv[1] if len(sys.argv) > 1 else "1"
    rate = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    
    print(f"Starting test with {replicas} replicas at {rate} req/s for {duration}s...")
    
    profiling_file = f"{RESULTS_DIR}/profiling_{replicas}_replicas_{rate}rps.csv"
    with open(profiling_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Pod", "CPU"])
        
        load_thread = threading.Thread(target=run_load, args=(rate, duration))
        load_thread.start()
        
        while load_thread.is_alive():
            time.sleep(5)
            ts = time.strftime("%H:%M:%S", time.localtime())
            cpu_data = get_pod_cpu()
            for pod, cpu in cpu_data.items():
                writer.writerow([ts, pod, cpu])
                
        load_thread.join()
    print("Test complete. Profiling data saved to", profiling_file)

if __name__ == "__main__":
    main()
