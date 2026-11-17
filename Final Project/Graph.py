
import csv
import matplotlib.pyplot as plt

files = []
speeds = []

with open("results.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if row["Operation"] == "Upload" or row["Operation"] == "Download":
            files.append(row["File Name"] + " " + row["Operation"])
            speeds.append(float(row["Speed (MB/s)"]))

if len(files) == 0:
    print("No transfer results found.")
else:
    plt.bar(files, speeds)

    plt.xlabel("Files")
    plt.ylabel("Speed (MB/s)")
    plt.title("Upload and Download Speeds")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig("transfer_speeds.png")
    plt.show()
