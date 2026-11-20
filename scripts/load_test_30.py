import urllib.request
import json
import collections
import random

url = "http://emi.local/api/emi"
results = []

print("Sending 30 requests through Ingress (http://emi.local)...")
print()

for i in range(1, 31):
    data = json.dumps({
        "principal": random.randint(100000, 1000000),
        "rate": round(random.uniform(5.0, 15.0), 2),
        "months": random.randint(12, 60)
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            pod_name = res_body.get('servedBy', 'Unknown').split(' ')[0]
            results.append(pod_name)
            print(f"Request {i:02d}: served by {pod_name}")
    except Exception as e:
        print(f"Request {i:02d}: Failed ({e})")

print()
print("--- Load Distribution Summary (3 Replicas) ---")
counts = collections.Counter(results)
for pod, count in counts.items():
    print(f"{pod}: {count} requests")
