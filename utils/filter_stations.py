#/usr/bin/python
import pandas as pd
import glob


input_name = "./input2007.text"
i = pd.read_csv(
    filepath_or_buffer = input_name,
    delimiter= " ",
    header= None,
    comment= "#"
)
i.columns = ["node", "network", "station", "start_d", "end_d"]

df = pd.DataFrame()
#df.columns = ["node", "network", "station", "start_d", "end_d"]

filepath = "./filter2007"
files = [f for f in glob.glob(filepath + "/*.text")]
for f in files:
    d = pd.read_csv(
        filepath_or_buffer = f,
        delimiter= " ",
        header= None,
        comment= "#"
    )
    d.columns = ["node", "network", "station"]
    print "d",d
    ee = i.loc[(i["network"].isin(d["network"].values) &
            i["station"].isin(d["station"].values) &
            i["node"].isin(d["node"].values))]
    df = df.append(ee, ignore_index=True)
    print "e",df

df = df.sort_values(by=["node", "network", "station"])
df.to_csv(
    path_or_buf = "{}_f.text".format(input_name.split(".text")[0]),
    sep = " ",
    index = False,
    header = None
    )