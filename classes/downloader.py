from setup_logger import logger
import obspy
from obspy.clients.fdsn import RoutingClient, Client
from obspy.clients.fdsn.client import FDSNException
import pandas as pd

class Downloader(object):
    def __init__(self, input_path):
        self._df = pd.read_csv(input_path, header = None, delimiter = " ", comment='#')
        self._df.columns = [ "client", "networkCode", "stationName", "start_time", "end_time" ]
        self._clients = {}
        self._token = ""

    def add_token(self, token):
        self._token = token
    
    def add_clients(self,list_of_clients):
        for client in list_of_clients:
            print client
            try:
            #if True:
                self._clients[client] = obspy.clients.fdsn.Client(client, eida_token = self._token)
            except obspy.clients.fdsn.client.FDSNException:
                print "Token is not accepted. Init %s wirhout token" % (client)
                self._clients[client] = obspy.clients.fdsn.Client(client)
        print self._clients

    def start_download(self):
        for index, row in self._df.iterrows():
            #print index, row
            t = obspy.core.UTCDateTime(row["start_time"])
            t_end = obspy.core.UTCDateTime(row["end_time"])
            while t <= t_end:
                print t
                t += 60*60*24