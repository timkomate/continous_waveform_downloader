import pandas as pd
import glob
import matplotlib.pyplot as plt
import numpy as np

log_dir = "./logs/"

logs = pd.DataFrame()

for file in glob.iglob("{}/*.log".format(log_dir)):
    df = pd.read_csv(
        filepath_or_buffer = file,
        delimiter= "::",
        comment= "#",
        header=None
    )
    logs = logs.append(df)

logs.columns = ["entry_date", "type", "script", "line_num", "file", "elapsed_time", "process_time"]
logs["entry_date"] = pd.to_datetime(logs["entry_date"], format ="%Y-%m-%d %H:%M:%S,%f")
print logs["entry_date"]



h = logs.loc[logs["process_time"] > 0]

n, bins, patches = plt.hist(logs["elapsed_time"].values, 100, normed=1, facecolor='green', alpha=0.75)
plt.xlabel("Elapsed Time")
plt.ylabel("frequency")
plt.title("sigma = {} mu = {}".format(np.std((logs["elapsed_time"].values)),np.mean((logs["elapsed_time"].values))))
#plt.axis([40, 160, 0, 0.03])
plt.grid(True)

plt.show()

n, bins, patches = plt.hist(h["process_time"].values, 200, normed=1, facecolor='green', alpha=0.75)

plt.xlabel("Processing Time")
plt.ylabel("frequency")
plt.title("sigma = {} mu = {}".format(np.std((h["process_time"].values)),np.mean((h["process_time"].values))))
#plt.axis([40, 160, 0, 0.03])
plt.grid(True)

plt.show()

n, bins, patches = plt.hist(h["elapsed_time"].values- h["process_time"], 100, normed=1, facecolor='green', alpha=0.75)

plt.xlabel("Downloading Time")
plt.ylabel("frequency")
#plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
#plt.axis([40, 160, 0, 0.03])
plt.grid(True)

plt.show()