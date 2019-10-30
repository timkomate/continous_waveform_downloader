from setup_logger import logger
import processing
import obspy
import os
from obspy.clients.fdsn import RoutingClient, Client
from obspy.clients.fdsn.client import FDSNException
import sys
import pandas as pd
import time, timeit
from scipy import io

class Downloader(object):
    def __init__(self, input_path):
        self._df = pd.read_csv(input_path, header = None, delimiter = " ", comment='#')
        self._df.columns = [ "client", "network", "station", "start_time", "end_time" ]
        self._clients = {}
        self._token = ""
        self._processing = ""
        self._response_flag = ""
        self._processing_time = -1
        self._error_code = 0

    def add_token(self, token):
        self._token = token
    
    def add_clients(self,list_of_clients):
        for client in list_of_clients:
            self.add_single_client(client)

    def add_single_client(self, client):
        print client
        try:
            self._clients[client] = obspy.clients.fdsn.Client(client, eida_token = self._token)
        except obspy.clients.fdsn.client.FDSNException:
            print "Token is not accepted. Init %s without token" % (client)
            self._clients[client] = obspy.clients.fdsn.Client(client)

    def start_download(self, dt, components, channels, max_gap, data_percentage, sleep_time, attempts):
        for index, row in self._df.iterrows():
            t = obspy.core.UTCDateTime(row["start_time"])
            t_end = obspy.core.UTCDateTime(row["end_time"])
            if(row["client"] not in self._clients):
                self.add_single_client(row["client"])
            for component in components:
                while t <= t_end:
                    start = timeit.default_timer()
                    self._error_code = 0
                    
                    waveform, inventory = self.get_waveform(
                        row = row,
                        t = t,
                        component = component,
                        channels = channels,
                        dt = dt, 
                        max_gap = max_gap, 
                        data_percentage = data_percentage, 
                        sleep_time = sleep_time, 
                        attempts = attempts
                    )
                    if (waveform is not None and inventory is not None):
                        waveform = self.process_waveform(waveform, inventory)
                        subpath = "%s/%s/%s/" % \
                            (component,t.year, t.datetime.strftime("%Y%m%d"))
                        filename = "%s.%s.%s_%s_%s" % \
                            (row["network"], row["station"], component, self._response_flag, t.datetime.strftime("%Y-%m-%d"))
                        print subpath, filename
                        self.save_waveform(
                            savedir = "./test/",
                            subdir = subpath,
                            filename = filename, 
                            waveform = waveform,
                            inventory = inventory
                        )
                        logger.debug("%s.%s.%s::%s::%s", row["network"],row["station"], t.strftime("%Y%m%d"), timeit.default_timer()-start, self._processing)
                    else:
                        logger.debug("%s.%s.%s::%s::%s", row["network"],row["station"], t.strftime("%Y%m%d"), timeit.default_timer()-start, self._error_code)
                    t += dt
                    
    
    def get_waveform(self, row, t, component, channels,
        dt = 86400, max_gap = 3600, data_percentage = 0.75, sleep_time = 1, attempts = 1):
        for channel in channels:
            con = "%sH%s" % (channel, component)
            attempt = 1
            while attempt <= attempts:
                try:
                    waveform = self._clients[row["client"]].get_waveforms(
                        network = row["network"], 
                        station = row["station"], 
                        location = '*', 
                        channel = con, 
                        starttime = t, 
                        endtime = t + dt, 
                        attach_response = True
                    )
                    waveform.merge(
                        method = 0,
                        fill_value = 0,
                        interpolation_samples = 5
                        )
                    waveform = waveform.pop()

                    inventory = self._clients[row["client"]].get_stations(
                        network = row["network"], 
                        station = row["station"], 
                        location = '*', 
                        channel = con, 
                        starttime = t, 
                        endtime = t + dt, 
                        level = "response"
                    )

                    return waveform, inventory
                except obspy.clients.fdsn.header.FDSNNoDataException:
                    self._error_code = -1
                except KeyboardInterrupt:
                    self._error_code = -3
                    sys.exit()
                except:
                    self._error_code = -2
                attempt += 1
        return None, None
    
    def process_waveform(self, waveform, inventory, sampling_rate, bandpass_freqmin, bandpass_freqmax):
        start = timeit.default_timer()
        waveform.interpolate(
            sampling_rate = sampling_rate,
            method = "weighted_average_slopes"
        )
        waveform.filter(
            type = "bandpass",
            freqmin = bandpass_freqmin, 
            freqmax = bandpass_freqmax
        )
        waveform.detrend(
            type = "linear"
        )
        waveform.remove_response(
            inventory = inventory
        )
        self._response_flag = "VEL"
        self._processing = timeit.default_timer() - start
        return waveform

    def save_waveform(self, savedir, subdir, filename, waveform, inventory):
        directory = "%s/%s" % (savedir, subdir)
        if not os.path.exists(directory):
            os.makedirs(directory)
        waveform_dictionary = {
            "processing": self._processing,
            "network": str(waveform.stats.network),
            "mseed": str(waveform.stats.mseed),
            "npts": float(waveform.stats.npts),
            "station": str(waveform.stats.station),
            "lat" : float(inventory[0][0].latitude),
            "lon" : float(inventory[0][0].longitude),
            "elevation" : float(inventory[0][0].elevation),
            "location": str(waveform.stats.location),
            "starttime": str(waveform.stats.starttime),
            "delta": float(waveform.stats.delta),
            "sampling_rate": float(waveform.stats.sampling_rate),
            "endtime": str(waveform.stats.endtime),
            "data": waveform.data,
            "channel": str(waveform.stats.channel)
        }
        save = "%s/%s" % (directory, filename)
        io.savemat(save,waveform_dictionary)

#TODO:
#Add more options via the config file.
#Do some additional quality checks.
#Check if file already exists.