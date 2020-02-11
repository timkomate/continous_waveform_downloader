#import matplotlib.pyplot as plt
import utilities
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
from scipy import signal, fftpack

from setup_logger import logger

class Downloader(object):
    def __init__(self, input_path):
        self._df = pd.read_csv(input_path, header = None, delimiter = " ", comment='#')
        self._df.columns = [ "client", "network", "station", "start_time", "end_time" ]
        self._clients = {}
        self._token = ""
        self._processing = ""
        self._processing_time = -1
        self._name_ext = "VEL" if parameter_init.processing else "RAW"
        self._name_ext += "tdn" if parameter_init.timedomain_normalization else ""
        self._name_ext += "wh_" if parameter_init.apply_whitening else "_"
        self._error_code = 0

    def add_token(self, token):
        self._token = token
    
    def add_clients(self,list_of_clients):
        for client in list_of_clients:
            self.add_single_client(client)

    def add_single_client(self, client):
        try:
            self._clients[client] = obspy.clients.fdsn.Client(client, eida_token = self._token)
        except obspy.clients.fdsn.client.FDSNException:
            print "Token is not accepted. Init %s without token" % (client)
            self._clients[client] = obspy.clients.fdsn.Client(client)
        except ValueError:
            print "Token does not exist. Init %s without token" % (client)
            self._clients[client] = obspy.clients.fdsn.Client(client)

    def start_download(self, dt = 86400, saving_directory = "./", components = ["Z"], channels = ["B", "H"], 
                        max_gap = 3600, data_percentage = 0.60, sleep_time = 0, attempts = 1, override = False,
                        processing = True, timedomain_normalization = False, resample = True, sampling_freq = 5,
                        date_format = "%Y%m%d", detrend_option = "linear", anti_aliasing_filter = [200,1], filter_order = 4,
                        zero_phase = True, filters = [[100,10], [10,5], [5,1]], envsmooth = 1500, env_exp = 1.5, 
                        min_weight = 0.1, taper_length_normalization = 1000, plot = False, apply_broadband_filter = False,
                        broadband_filter = [200,1], apply_whitening = False, spectrumexp = 0.7, espwhitening = 0.05, 
                        taper_length_whitening = 100):
        for index, row in self._df.iterrows():
            print "{}.{}".format(row["network"],row["station"])
            t_end = obspy.core.UTCDateTime(row["end_time"])
            if(row["client"] not in self._clients):
                self.add_single_client(row["client"])
            for component in components:
                t = obspy.core.UTCDateTime(row["start_time"])
                while t <= t_end:
                    subpath = "%s/%s/%s/" % (component,t.year, t.datetime.strftime(date_format))
                    filename = "%s.%s.%s_%s%s" % \
                        (row["network"], row["station"], component, self._name_ext, t.datetime.strftime(date_format))
                    start = timeit.default_timer()
                    self._error_code = 0
                    message = "{}::{}::{}::{}::{}".format(row["client"],row["network"],row["station"], component, t.strftime(date_format))
                    if (override or not os.path.exists("%s/%s/%s.mat" % (saving_directory, subpath, filename))):
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
                                processing = processing,
                                normalization = timedomain_normalization,
                                resample = resample,
                                sampling_rate = sampling_freq, 
                                detrend_option = detrend_option,
                                anti_aliasing_filter = anti_aliasing_filter,
                                filter_order = filter_order,
                                zero_phase = zero_phase,
                                filters = filters,
                                envsmooth = envsmooth, 
                                env_exp = env_exp, 
                                min_weight = min_weight, 
                                taper_length = taper_length_normalization, 
                                plot = plot, 
                                apply_broadband_filter = apply_broadband_filter,
                                broadband_filter = broadband_filter,
                                apply_whitening = apply_whitening,
                                spectrumexp = spectrumexp, 
                                espwhitening = espwhitening, 
                                taper_length_whitening = taper_length_whitening
                            )
                            if (waveform is not None):
                                if (not (~np.isfinite(waveform.data)).any()):
                                    self.save_waveform(
                                        savedir = parameter_init.saving_directory,
                                        subdir = subpath,
                                        filename = filename, 
                                        waveform = waveform,
                                        inventory = inventory
                                    )
                                    logger.info("%s::%s::%s",message, timeit.default_timer()-start, self._processing_time)
                                else:
                                    self._error_code = -7
                                    logger.info("%s::%s::%s", message, timeit.default_timer()-start, self._error_code)
                            else:
                                self._error_code = -6
                                logger.info("%s::%s::%s", message, timeit.default_timer()-start, self._error_code)
                        else:
                            logger.info("%s::%s::%s", message, timeit.default_timer()-start, self._error_code)
                    else:
                        self._error_code = -4
                        logger.info("%s::%s::%s", message, timeit.default_timer()-start, self._error_code)
                    t += dt               
    
    def get_waveform(self, row, t, component, channels, dt, max_gap, data_percentage, sleep_time, attempts):
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
                        attach_response = False
                    )
                    if (not self.waveform_quality(waveform, max_gap, data_percentage, dt)):
                        raise Quality_error([row["network"], row["station"], t])

                    waveform.merge(fill_value = "interpolate")
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
                except Quality_error:
                    self._error_code = -5
                except KeyboardInterrupt:
                    self._error_code = -3
                except:
                    self._error_code = -2
                attempt += 1
                time.sleep(sleep_time)
        return None, None
    
    def process_waveform(self, waveform, inventory, processing = True, normalization = False, 
                        resample = True, sampling_rate = 5, detrend_option = "linear", 
                        anti_aliasing_filter = 1, filter_order = 4, zero_phase = True, 
                        filters = [[100,10], [10,5], [5,1]], envsmooth = 1500, 
                        env_exp = 1.5, min_weight = 0.1, taper_length = 1000, plot = False, 
                        apply_broadband_filter = False, broadband_filter = [200,1], 
                        apply_whitening = False, spectrumexp = 0.7, espwhitening = 0.05, 
                        taper_length_whitening = 100):
        start = timeit.default_timer()
        self._processing = ""
        try:
        #if (True):
            if processing:
                self._processing += "Detrend -> "
                waveform.detrend(
                    type = detrend_option
                )
                self._processing += "Demean -> "
                waveform.detrend(
                    type = "demean"
                )
                self._processing += "Cosine type taper: 0.05 % ->"
                waveform.taper(
                    type = "cosine",
                    max_percentage = 0.05
                )
                
                self._processing += "lowpass filter at: {} sec. Filter-order: {}, zerophase: {} -> ".format(
                    anti_aliasing_filter, filter_order, zero_phase
                )
                waveform.filter(
                    type = "lowpass",
                    freq = 1./anti_aliasing_filter, 
                    corners = filter_order,
                    zerophase = zero_phase
                )
                if (resample and waveform.stats.sampling_rate > sampling_rate):
                    self._processing += "resample to: {} Hz -> ".format(sampling_rate)
                    waveform.interpolate(
                        sampling_rate = sampling_rate,
                        method = "weighted_average_slopes"
                    )
                self._processing += "remove response -> "
                waveform.remove_response(
                    inventory = inventory
                )

                if (apply_broadband_filter):
                    self._processing += "bandpass filter between: {} and {} sec. Filter-order: {}, zerophase: {} -> ".format(
                        broadband_filter[0], broadband_filter[1], filter_order, zero_phase
                    )
                    waveform.filter(
                        type = "bandpass",
                        freqmin = 1./broadband_filter[0], 
                        freqmax = 1./broadband_filter[1], 
                        corners = filter_order,
                        zerophase = zero_phase
                    )

                if (normalization):
                    self._processing += "running absolute mean normalization -> "
                    #print "time domain normalization..."
                    waveform.data = utilities.running_absolute_mean(
                        waveform = waveform,
                        filters = filters,
                        filter_order = filter_order,
                        envsmooth = envsmooth,
                        env_exp = env_exp,
                        min_weight = min_weight, 
                        taper_length = taper_length, 
                        plot = plot,
                        apply_broadband_filter = apply_broadband_filter,
                        broadband_filter = broadband_filter
                    )
                
                if (apply_whitening):
                    #print "whitening... does not tested properly"
                    self._processing += "spectral whitening -> "
                    waveform.data = utilities.spectral_whitening(
                        data = waveform.data,
                        sampling_rate = waveform.stats.sampling_rate,
                        spectrumexp = spectrumexp,
                        espwhitening = espwhitening,
                        taper_length = taper_length_whitening,
                        apply_broadband_filter = apply_broadband_filter,
                        broadband_filter = broadband_filter,
                        filter_order = filter_order,
                        plot = plot
                    )
            else:
                self._processing += "remove sensitivity ->"
                waveform.remove_sensitivity()

            self._processing_time = timeit.default_timer() - start
            self._processing += "processing time: {} sec".format(self._processing_time)
            return waveform
        except:
            self._processing_time = timeit.default_timer() - start
            return None

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