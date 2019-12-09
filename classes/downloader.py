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
from utilities import downweight_ends
from scipy import signal, fftpack

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
	except ValueError:
            print "Token does not exist. Init %s without token" % (client)
	    self._clients[client] = obspy.clients.fdsn.Client(client)

    def start_download(self, dt, components, channels, max_gap, data_percentage, sleep_time, attempts):
        for index, row in self._df.iterrows():
            if(row["client"] not in self._clients):
                self.add_single_client(row["client"])
            for component in components:
                t = obspy.core.UTCDateTime(row["start_time"])
                t_end = obspy.core.UTCDateTime(row["end_time"])
                while t <= t_end:
                    subpath = "%s/%s/%s/" % (component,t.year, t.datetime.strftime("%Y%m%d"))
                    filename = "%s.%s.%s_%s%s" % \
                        (row["network"], row["station"], component, self._name_ext, t.datetime.strftime("%Y-%m-%d"))
                    print filename
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
                                normalization = parameter_init.timedomain_normalization,
                                sampling_rate = parameter_init.sampling_freq, 
                                detrend_option = parameter_init.detrend_option,
                                bandpass_freqmin = parameter_init.bandpass_freqmin, 
                                bandpass_freqmax = parameter_init.bandpass_freqmax,
                                filters = parameter_init.filters,
                                envsmooth = parameter_init.envsmooth, 
                                env_exp = parameter_init.env_exp, 
                                min_weight = parameter_init.min_weight, 
                                taper_length = parameter_init.taper_length, 
                                plot = parameter_init.plot, 
                                broadband_filter = parameter_init.broadband_filter
                            )
                            if (waveform is not None):
                                self.save_waveform(
                                    savedir = parameter_init.saving_directory,
                                    subdir = subpath,
                                    filename = filename, 
                                    waveform = waveform,
                                    inventory = inventory
                                )
                                logger.debug("%s.%s.%s::%s::%s", row["network"],row["station"], t.strftime("%Y%m%d"), timeit.default_timer()-start, self._processing)
                            else:
                                self._error_code = -6
                                logger.debug("%s.%s.%s::%s::%s", row["network"],row["station"], t.strftime("%Y%m%d"), timeit.default_timer()-start, self._error_code)
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
    
    def process_waveform(self, waveform, inventory, processing, normalization, sampling_rate, detrend_option, bandpass_freqmin, bandpass_freqmax,
        filters = [[30,1]],envsmooth = 1500, env_exp = 1.5, min_weight = 0.1, taper_length = 1000, plot = False, broadband_filter = [200,1]):
        start = timeit.default_timer()
        try:
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
                if (normalization):
                    print "time domain normalization..."
                    waveform.data = self.running_absolute_mean(
                        waveform = waveform,
                        filters = filters,
                        envsmooth = envsmooth, 
                        env_exp = env_exp,
                        min_weight = min_weight, 
                        taper_length = taper_length, 
                        plot = plot,
                        broadband_filter = broadband_filter
                    )
            else:
                waveform.remove_sensitivity()

            self._processing = timeit.default_timer() - start
            return waveform
        except:
            self._processing = timeit.default_timer() - start
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

    def running_absolute_mean(self, waveform, filters, envsmooth = 1500, env_exp = 1.5, 
                        min_weight = 0.1, taper_length = 1000, plot = False,
                        broadband_filter = [200,1]):
        data = (signal.detrend(waveform.data, type="linear" )) / np.power(10,9)
        nb = np.floor(envsmooth/waveform.stats.delta)
        weight = np.ones((data.shape[0]))
        boxc = np.ones((int(nb)))/nb
        nyf = (1./2)*waveform.stats.sampling_rate
        if (plot):
            plt.plot(data)
            plt.title("unfiltered data")
            plt.show()
        [b,a] = signal.butter(
            N = 3,
            Wn = [1./broadband_filter[0]/nyf, 1./broadband_filter[1]/nyf], 
            btype='bandpass'
        )
        data = signal.filtfilt(
            b = b,
            a = a,
            x = data)
        for filter in filters:
            print filter
            [b,a] = signal.butter(3,[1./filter[0]/nyf, 1./filter[1]/nyf], btype='bandpass')
            filtered_data = downweight_ends(signal.filtfilt(b,a,data), wlength = taper_length * waveform.stats.sampling_rate)
            if (plot):
                plt.plot(filtered_data)
                plt.title("filtered data")
                plt.show()
            data_env = signal.convolve(abs(filtered_data),boxc,method="fft")
            data_env = data_env[boxc.shape[0]/ 2 -1: -boxc.shape[0]/ 2]
            if (plot):
                plt.plot(data_env)
                plt.title("envelope")
                plt.show()
            #print data_env.shape, self._data.shape
            data_exponent = np.power(data_env, env_exp)
            weight = weight * data_exponent / np.mean(data_exponent)
            if (plot):
                plt.plot(weight)
                plt.title("weights")
                plt.show()
        water_level = np.mean(weight) * min_weight
        weight[weight < water_level] = water_level
        nb = 2*int(taper_length*waveform.stats.sampling_rate)
        weight[:nb] = np.mean(weight)
        weight[-nb:] = np.mean(weight)
        if (plot):
            plt.plot(weight)
            plt.title("final weights")
            plt.show()
        data = downweight_ends((data / weight),wlength = taper_length * waveform.stats.sampling_rate) 
        if (plot):
            plt.plot(data)
            plt.title("filtered data")
            plt.show()
        return data

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
#
