import urllib.request
import json
import random
import time
import subprocess
import threading
import csv
import os

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

def run_phase(rate, duration, phase_name):
    print(f"Phase: {phase_name} at {rate} req/s for {duration}s")
    total = rate * duration
    interval = 1.0 / rate
    start = time.time()
    
    for i in range(total):
        next_t = start + (i * interval)
        now = time.time()
        if next_t > now:
            time.sleep(next_t - now)
        send_request()

def get_hpa_info():
    try:
        output = subprocess.check_output(["kubectl", "get", "hpa", "emi-web", "-n", "emi", "--no-headers"]).decode()
        parts = output.split()
        replicas = parts[6] if len(parts) > 6 else "?"
        cpu = parts[3] if len(parts) > 3 else "?"
        return replicas, cpu
    except:
        return "?", "?"

def main():
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        
    hpa_file = f"{RESULTS_DIR}/autoscaling_hpa.csv"
    with open(hpa_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Replicas", "CPU_Percentage"])
        
        start_time = time.time()
        
        # Phase 1: 10 req/s for 2 min
        threading.Thread(target=run_phase, args=(10, 120, "Low Load")).start()
        for _ in range(8):
            time.sleep(15)
            ts = time.strftime("%H:%M:%S", time.localtime())
            reps, cpu = get_hpa_info()
            writer.writerow([ts, reps, cpu])
        
        # Phase 2: 100 req/s for 5 min
        threading.Thread(target=run_phase, args=(100, 300, "High Load")).start()
        for _ in range(20):
            time.sleep(15)
            ts = time.strftime("%H:%M:%S", time.localtime())
            reps, cpu = get_hpa_info()
            writer.writerow([ts, reps, cpu])
            
        # Phase 3: 10 req/s for 3 min
        threading.Thread(target=run_phase, args=(10, 180, "Cool Down")).start()
        for _ in range(12):
            time.sleep(15)
            ts = time.strftime("%H:%M:%S", time.localtime())
            reps, cpu = get_hpa_info()
            writer.writerow([ts, reps, cpu])
            
    print("Autoscaling test complete. Data saved to", hpa_file)

if __name__ == "__main__":
    main()
