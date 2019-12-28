import multiprocessing
from classes import downloader, metadata, parameter_init

class Download_driver(object):
    def __init__(self, filenames):
        self._filenames = filenames

    def __call__(self, filename):
        self.go(filename)

    def make_metadata(self):
        if (parameter_init.download_metadata):
            print "Accessign metadata information..."
            metadata = metadata.Metadata(
                lat = parameter_init.latitude,
                lon = parameter_init.longitude,
                max_radius = parameter_init.max_radius,
                start_year = parameter_init.start_year,
                end_year = parameter_init.end_year,
            )
            metadata.save_json(save_path = parameter_init.json_path)
            metadata.make_inputfile(save_path = parameter_init.station_list_path)
            metadata.extract_station_coordinates(save_path = parameter_init.coordinate_output)
            print "Metatada has been saved!"

    def start(self, core_number = multiprocessing.cpu_count()):
        if core_number < 1:
            core_number = multiprocessing.cpu_count()
        print "Number of cores:", core_number
        pool = multiprocessing.Pool(core_number)
        pool.map(self, self._filenames)
        pool.close()
        pool.join()
    
    def go(self, input_name):
        print input_name
        dw = downloader.Downloader(input_path = input_name)
        dw.add_token(token = parameter_init.token_path)
        dw.start_download(
            dt = parameter_init.dt,
            saving_directory=parameter_init.saving_directory,
            components = parameter_init.components,
            channels = parameter_init.channels,
            max_gap = parameter_init.max_gap,
            data_percentage = parameter_init.data_percentage, 
            sleep_time = parameter_init.sleep_time, 
            attempts = parameter_init.attempts,
            override=parameter_init.override,
            processing=parameter_init.processing,
            timedomain_normalization=parameter_init.timedomain_normalization,
            resample=parameter_init.resample,
            sampling_freq=parameter_init.sampling_freq,
            detrend_option=parameter_init.detrend_option,
            anti_aliasing_filter=parameter_init.anti_aliasing_filter,
            filter_order=parameter_init.filter_order,
            zero_phase=parameter_init.zero_phase,
            filters=parameter_init.filters,
            envsmooth=parameter_init.envsmooth,
            env_exp=parameter_init.env_exp,
            min_weight=parameter_init.min_weight,
            taper_length_normalization=parameter_init.taper_length_tdn,
            plot=parameter_init.plot,
            apply_broadband_filter=parameter_init.apply_broadband_filter,
            broadband_filter=parameter_init.broadband_filter,
            apply_whitening=parameter_init.apply_whitening,
            spectrumexp=parameter_init.spectrumexp,
            espwhitening=parameter_init.espwhitening,
            taper_length_whitening=parameter_init.taper_length_whitening
        )