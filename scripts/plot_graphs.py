import matplotlib.pyplot as plt
import csv
import os

RESULTS_DIR = "results"

def plot_graph1():
    # Dummy data for Graph 1 (Aap apne real response time data se replace kar sakti hain)
    rates = [10, 25, 50, 100, 200]
    plt.plot(rates, [20, 25, 30, 50, 80], label="1 Replica", marker='o')
    plt.plot(rates, [15, 20, 25, 35, 50], label="2 Replicas", marker='s')
    plt.plot(rates, [10, 15, 20, 25, 30], label="3 Replicas", marker='^')
    plt.xlabel("Request Rate (req/s)")
    plt.ylabel("Average Response Time (ms)")
    plt.title("Graph 1: Response Time vs Request Rate")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{RESULTS_DIR}/graph1.png")
    plt.close()
    print("Graph 1 saved to results/graph1.png")

def plot_graph2():
    file = f"{RESULTS_DIR}/profiling_3_replicas_100rps.csv"
    if not os.path.exists(file):
        print("File not found:", file)
        return
        
    times = []
    pods = {}
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = row["Timestamp"]
            pod = row["Pod"]
            cpu = float(row["CPU"].replace("m", ""))
            
            if t not in times:
                times.append(t)
            if pod not in pods:
                pods[pod] = []
            while len(pods[pod]) < len(times) - 1:
                pods[pod].append(0)
            pods[pod].append(cpu)
    
    for pod, cpu_vals in pods.items():
        plt.plot(times, cpu_vals, label=pod)
    
    plt.xlabel("Time")
    plt.ylabel("CPU (millicores)")
    plt.title("Graph 2: CPU Utilization (3 Replicas, 100 req/s)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/graph2.png")
    plt.close()
    print("Graph 2 saved to results/graph2.png")

def plot_graph3():
    file = f"{RESULTS_DIR}/autoscaling_hpa.csv"
    if not os.path.exists(file):
        print("File not found:", file)
        return
        
    times = []
    replicas = []
    cpus = []
    
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(row["Timestamp"])
            replicas.append(int(row["Replicas"]))
            cpu = float(row["CPU_Percentage"].replace("%", "").split("/")[0])
            cpus.append(cpu)
            
    fig, ax1 = plt.subplots()
    
    color = 'tab:red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('CPU (%)', color=color)
    ax1.plot(times, cpus, color=color, label="CPU")
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(times[::4])  # Show every 4th label
    ax1.set_xticklabels(times[::4], rotation=45)
    
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Replicas', color=color)
    ax2.plot(times, replicas, color=color, linestyle='--', label="Replicas")
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title("Graph 3: Autoscaling Test")
    fig.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/graph3.png")
    plt.close()
    print("Graph 3 saved to results/graph3.png")

if __name__ == "__main__":
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    plot_graph1()
    plot_graph2()
    plot_graph3()
    print("All graphs generated in results/ folder.")
