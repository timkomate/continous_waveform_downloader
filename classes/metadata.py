from obspy.clients.fdsn import RoutingClient, Client
import obspy
from setup_logger import logger
import json

class Metadata(object):
    def __init__(self, lat, lon, radius, start_year, end_year, token_path, channel = "*H*", ):
        #client = obspy.clients.fdsn.RoutingClient("eida-routing", credentials={'EIDA_TOKEN': '/home/mate/PhD/codes/continous_waveform_downloader/eidatoken'})
        client = obspy.clients.fdsn.Client("GFZ")
        self._inv = client.get_stations(
            network = "*",
            channel = channel,
            starttime = start_year,
            endtime = end_year,
            latitude = lat, 
            longitude = lon,
            level = "channel",
            maxradius = radius
        )
    
    def save_json(self, save_path):
        with open(save_path, 'w') as fp:
            json.dump(self._inv, fp, sort_keys=True, indent=2)
    
    def save_inventory(self, save_path, format = "STATIONXML"):
        self._inv.write(
            path_or_file_object = save_path,
            format = format
        )  
    
    def read_inv(self, load_path):
        self._inv = obspy.read_inventory(load_path)

    def get_inventory(self):
        return self._inv

    

