import pandas as pd
import numpy as np
import obspy
from obspy.clients.fdsn import RoutingClient, Client
import glob
import os

def get_inventory(clients, row, t_start, t_end, component, channels):
    for channel in channels:
        con = "{}H{}".format(channel, component)
        try:
            inventory = clients[row["client"]].get_stations(
                network = row["network"], 
                station = row["station"], 
                location = '*', 
                channel = con, 
                starttime = t_start, 
                endtime = t_end, 
                level = "response"
            )

            return inventory
        except:
            return None

if __name__ == "__main__":
    for filepath in glob.iglob('./response/*.resp'):
        save_path = "./response/plots/"
        print(filepath)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        inv = obspy.core.inventory.inventory.read_inventory(filepath)
        for network in inv:
            print network
            for station in network:
                print station
                for cha in station:
                    a = inv.plot_response(
                        network = network.code,
                        station = station.code,
                        channel = "[BH]H?",
                        min_freq = 0.001,
                        outfile = "{}/{}_{}.png".format(save_path,network.code, station.code)
                    )
                    #del a
                    break