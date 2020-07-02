from __future__ import print_function
from classes import downloader, download_driver, parameter_init
import pandas as pd
import numpy as np
import os, glob

try:
    df = pd.read_csv(parameter_init.station_input_path, header = None, delimiter = " ", comment='#')
    df.columns = [ "client", "network", "station", "start_time", "end_time" ]
    df = np.array_split(df,parameter_init.number_of_cpus)
    dw_d = download_driver.Download_driver(df)
    dw_d.start(core_number = parameter_init.number_of_cpus)
except IOError as e:
    print(e)
