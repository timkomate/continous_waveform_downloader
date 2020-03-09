import pandas as pd
import numpy as np
import obspy
from obspy.clients.fdsn import RoutingClient, Client
import glob
import os
import matplotlib.pyplot as plt

if __name__ == "__main__":
    year = "2009"
    for filepath in glob.iglob('./response/{}/*.resp'.format(year)):
        node_name = filepath.split("/")[-1].split(".")[0]
        save_path = "./response/{}/plots/{}".format(year,node_name)
        print(filepath)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        inv = obspy.core.inventory.inventory.read_inventory(filepath)
        for network in inv:
            #print network
            for station in network:
                print station
                try:
                    a = inv.plot_response(
                        network = network.code,
                        station = station.code,
                        channel = "[BH]H?",
                        min_freq = 0.001,
                        outfile = "{}/{}_{}_{}.png".format(save_path,node_name,network.code, station.code)
                    )
                    plt.close("all")
                except StopIteration as e:
                    print "{}-{} failed: {}".format(network.code, station.code, e)
                    pass
                except ValueError as e:
                    print "{}-{} failed: {}".format(network.code, station.code, e)
                    pass
                except:
                    print "{}-{} failed:".format(network.code, station.code)
