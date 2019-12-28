import numpy as np
import math
from scipy import signal, fftpack

def downweight_ends(data, wlength):
    w = (1 - np.cos((math.pi / wlength) * (np.arange(0,wlength,1) + 1)))/2
    data[0:int(wlength)] = data[0:int(wlength)]*w
    w = np.flipud(w)
    data[-int(wlength):] = data[-int(wlength):]*w
    return data

def nextpow2(x):
    return 1<<(x-1).bit_length()


def running_absolute_mean(waveform, filters, filter_order = 4, envsmooth = 1500, 
                    env_exp = 1.5, min_weight = 0.1, taper_length = 1000, plot = False,
                    apply_broadband_filter = True, broadband_filter = [200,1]):
    
    data = (signal.detrend(waveform.data, type="linear" )) / np.power(10,9)
    nb = np.floor(envsmooth/waveform.stats.delta)
    weight = np.ones((data.shape[0]))
    boxc = np.ones((int(nb)))/nb
    nyf = (1./2)*waveform.stats.sampling_rate
    if (plot):
        plt.plot(data)
        plt.title("unfiltered data")
        plt.show()
    if (apply_broadband_filter):
        [b,a] = signal.butter(
            N = filter_order,
            Wn = [1./broadband_filter[0]/nyf, 1./broadband_filter[1]/nyf], 
            btype='bandpass'
        )
        data = signal.filtfilt(
            b = b,
            a = a,
            x = data
        )
    for filter in filters:
        [b,a] = signal.butter(
            N = filter_order,
            Wn = [1./filter[0]/nyf, 1./filter[1]/nyf], 
            btype='bandpass'
        )
        filtered_data = signal.filtfilt(
            b = b,
            a = a,
            x = data
        )
        filtered_data = downweight_ends(
            data = filtered_data, 
            wlength = taper_length * waveform.stats.sampling_rate
        )
        if (plot):
            plt.plot(filtered_data)
            plt.title("filtered data")
            plt.show()

        data_env = signal.convolve(
            in1 = abs(filtered_data),
            in2 = boxc,
            method="fft"
        )
        data_env = data_env[boxc.shape[0]/ 2 -1: -boxc.shape[0]/ 2]
        if (plot):
            plt.plot(data_env)
            plt.title("envelope")
            plt.show()
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
    data = downweight_ends(
        data = (data / weight),
        wlength = taper_length * waveform.stats.sampling_rate
    )
    if (plot):
        plt.plot(data)
        plt.title("filtered data")
        plt.show()

    return data

def spectral_whitening( data, sampling_rate, spectrumexp = 0.7, 
                        espwhitening = 0.05, taper_length = 100, 
                        apply_broadband_filter = True, broadband_filter = [200,1], 
                        filter_order = 4, plot = False):
    if (plot):
        plt.plot(data)
        plt.title("original dataset")
        plt.show()
        
    data = signal.detrend(
        data = data,
        type="linear"
    )
    spectrum = np.fft.rfft(
        a = data,
        n= nextpow2(len(data))
    )
    spectrum_abs = np.abs(spectrum)
    if (plot):
        f = np.fft.rfftfreq(len(data), d=1./sampling_rate)
        plt.plot(f,spectrum)
        plt.plot(f,spectrum_abs)
        plt.title("specrtum and ampl. spectrum")
        plt.show()
        
    water_level = np.mean(spectrum_abs) * espwhitening
    spectrum_abs[(spectrum_abs < water_level)] = water_level
        
    if (plot):
        plt.plot(f,spectrum_abs)
        plt.title("spectrum after water level")
        plt.show()
        fig, axs = plt.subplots(3)
        fig.suptitle('Vertically stacked subplots')
        axs[0].plot(spectrum)
        axs[1].plot(np.power(spectrum_abs,spectrumexp))
        axs[2].plot(spectrum_abs)
        plt.show()
        
    #whitening
    spectrum = np.divide(spectrum, np.power(spectrum_abs,spectrumexp))
    #spectrum = downweight_ends(spectrum, wlength = (taper_length * sampling_rate))
    spectrum[0] = 0

    if (plot):
        plt.plot(f,np.abs(spectrum))
        plt.title("spectrum after whitening")
        plt.show()

    whitened = np.fft.irfft(
        a = spectrum,
        #n = len(data)
    )
        
    whitened = signal.detrend(
        data = whitened,
        type="linear"
    )
        
    whitened =  downweight_ends(
        data = whitened,
        wlength= taper_length * sampling_rate
    )
    
    if (apply_broadband_filter):
        nyf = (1./2) * sampling_rate
        [b,a] = signal.butter(
            N = filter_order,
            Wn = [(1./broadband_filter[0])/nyf,(1./broadband_filter[1])/nyf], 
            btype='bandpass'
        )
        whitened = signal.filtfilt(
            b = b,
            a = a,
            x = whitened
        )

    if (plot):
        plt.plot(whitened)
        plt.title("whitened signal after filtering")
        plt.show()
    #remove mean
    whitened = whitened * np.mean(np.abs(whitened))
    whitened = np.append(whitened, 0)
    return whitened