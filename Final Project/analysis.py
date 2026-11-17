
import csv
import time
import threading

lock = threading.Lock()


# Calculate transfer speed
def calculate_speed(file_size, transfer_time):
    if transfer_time <= 0:
        return 0

    return round((file_size / 1000000) / transfer_time, 2)


# Measure response time
def measure_response_time(start_time):
    return round((time.perf_counter() - start_time) * 1000, 2)


# Save results
def save_results(operation, file_name, file_size, transfer_time,
                 response_time=0, client=""):

    speed = calculate_speed(file_size, transfer_time)

    with lock:
        with open("results.csv", "a", newline="") as file:
            writer = csv.writer(file)

            writer.writerow([
                operation,
                file_name,
                round(file_size / 1000000, 2),
                round(transfer_time, 2),
                speed,
                round(response_time, 2),
                client
            ])

    print(operation, file_name, speed, "MB/s")


# Start analysis with server
def start_analysis():
    with lock:
        with open("results.csv", "w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow([
                "Operation",
                "File Name",
                "File Size (MB)",
                "Time (seconds)",
                "Speed (MB/s)",
                "Response Time (ms)",
                "Client"
            ])

    print("Network Analysis Started")


