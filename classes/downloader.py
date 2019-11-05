from setup_logger import logger
import parameter_init
import obspy
import os
import numpy as np
from obspy.clients.fdsn import RoutingClient, Client
from obspy.clients.fdsn.client import FDSNException
import sys
import pandas as pd
import time, timeit
from scipy import io
from quality_error import Quality_error

class Downloader(object):
    def __init__(self, input_path):
        self._df = pd.read_csv(input_path, header = None, delimiter = " ", comment='#')
        self._df.columns = [ "client", "network", "station", "start_time", "end_time" ]
        self._clients = {}
        self._token = ""
        self._processing = -1
        self._name_ext = "VEL" if parameter_init.processing else "RAW"
        self._name_ext += "tdn_" if parameter_init.timedomain_normalization else "_"
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
                    subpath = "%s/%s/%s/" % (component,t.year, t.datetime.strftime("%Y%m%d"))
                    filename = "%s.%s.%s_%s%s" % \
                        (row["network"], row["station"], component, self._name_ext, t.datetime.strftime("%Y-%m-%d"))
                    start = timeit.default_timer()
                    self._error_code = 0
                    if (parameter_init.override or not os.path.exists("%s/%s/%s.mat" % (parameter_init.saving_directory, subpath, filename))):
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
                            waveform = self.process_waveform(
                                waveform = waveform, 
                                inventory = inventory,
                                processing = parameter_init.processing,
                                sampling_rate = parameter_init.sampling_freq, 
                                detrend_option = parameter_init.detrend_option,
                                bandpass_freqmin = parameter_init.bandpass_freqmin, 
                                bandpass_freqmax = parameter_init.bandpass_freqmax
                                )
                            self.save_waveform(
                                savedir = parameter_init.saving_directory,
                                subdir = subpath,
                                filename = filename, 
                                waveform = waveform,
                                inventory = inventory
                            )
                            logger.debug("%s.%s.%s::%s::%s", row["network"],row["station"], t.strftime("%Y%m%d"), timeit.default_timer()-start, self._processing)
                        else:
                            logger.debug("%s.%s.%s::%s::%s", row["network"],row["station"], t.strftime("%Y%m%d"), timeit.default_timer()-start, self._error_code)
                    else:
                        self._error_code = -4
                        logger.debug("%s.%s.%s::%s::%s", row["network"],row["station"], t.strftime("%Y%m%d"), timeit.default_timer()-start, self._error_code)
                    t += dt
                    #sleep(3)
                    
    
    def get_waveform(self, row, t, component, channels, dt, max_gap, data_percentage, sleep_time, attempts):
        for channel in channels:
            con = "%sH%s" % (channel, component)
            attempt = 1
            while attempt <= attempts:
                try:
                #if True:
                    waveform = self._clients[row["client"]].get_waveforms(
                        network = row["network"], 
                        station = row["station"], 
                        location = '*', 
                        channel = con, 
                        starttime = t, 
                        endtime = t + dt, 
                        attach_response = True
                    )
                    if (not self.waveform_quality(waveform, max_gap, data_percentage, dt)):
                        raise Quality_error([row["network"], row["station"], t])

                    """waveform.merge(
                        method = 0,
                        fill_value = 0,
                        interpolation_samples = 5
                        )"""
                    waveform.merge(fill_value = "interpolate")
                    waveform = waveform.pop()
                    #waveform.plot()

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
                except Quality_error:
                    self._error_code = -5
                except KeyboardInterrupt:
                    self._error_code = -3
                except:
                    self._error_code = -2
                attempt += 1
        return None, None
    
    def process_waveform(self, waveform, inventory, processing, sampling_rate, detrend_option, bandpass_freqmin, bandpass_freqmax):
        start = timeit.default_timer()
        
        if processing:
            waveform.detrend(
                type = detrend_option
            )

            waveform.detrend(
                type = "demean"
            )

            waveform.filter(
                type = "bandpass",
                freqmin = bandpass_freqmin, 
                freqmax = bandpass_freqmax
            )

            waveform.interpolate(
                sampling_rate = sampling_rate,
                method = "weighted_average_slopes"
            )
            waveform.remove_response(
                inventory = inventory
            )
        else:
            waveform.remove_sensitivity()

        self._processing = timeit.default_timer() - start
        return waveform

    @staticmethod
    def get_num_samples(stream):
        s = 0
        for tr in stream:
            s += tr.count()
        return float(s)

    @staticmethod
    def get_max_gap(gap_list):
        max_gap = 0
        for i in gap_list:
            if(i[-1] > max_gap):
                max_gap = i[-1]
        return max_gap

    def waveform_quality(self, waveform, max_gap, data_percentage, dt):
        s = Downloader.get_num_samples(waveform)
        gap = Downloader.get_max_gap(waveform.get_gaps())
        if (gap < waveform[0].stats.sampling_rate*max_gap and s / (waveform[0].stats.sampling_rate * dt) > data_percentage):
            return True
        return False

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
        print "save:", save
        io.savemat(save,waveform_dictionary)

#TODO:
#timedomain normalization