
import csv
import matplotlib.pyplot as plt

# Lists for the graph data
files = []
speeds = []
times = []

# Read the results from the CSV file
with open("results.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if row["Operation"] == "Upload" or row["Operation"] == "Download":
            operation = row["Operation"]
            filename = row["File Name"]

            # Shorten long filenames for the graphs
            if len(filename) > 20:
                filename = filename[:17] + "..."

            files.append(operation + "\n" + filename)
            speeds.append(float(row["Speed (MB/s)"]))
            times.append(float(row["Time (seconds)"]))

# Check that results were found
if len(files) == 0:
    print("No transfer results found.")

else:
    # Graph 1: Upload and Download Speeds
    plt.figure(figsize=(9, 5))
    plt.bar(files, speeds)

    plt.title("Upload and Download Speeds")
    plt.xlabel("File Transfers")
    plt.ylabel("Speed (MB/s)")

    plt.tight_layout()
    plt.savefig("transfer_speeds.png")
    plt.show()
