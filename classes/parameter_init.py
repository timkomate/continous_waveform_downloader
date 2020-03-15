import ConfigParser

config = ConfigParser.ConfigParser()
config.read("./config.cfg")

#[METADATA]
download_metadata = config.getboolean("METADATA", "download_metadata")
save_response = config.getboolean("METADATA", "save_response")
EIDA_nodes = config.get("METADATA", "EIDA_nodes").split(',')
network = config.get("METADATA", "network")
meta_channels = config.get("METADATA", "meta_channels")
latitude = config.getfloat("METADATA", "latitude")
longitude = config.getfloat("METADATA", "longitude")
max_radius = config.getfloat("METADATA", "max_radius")
start_year = config.get("METADATA", "start_year")
end_year = config.get("METADATA", "end_year")
json_path = config.get("METADATA", "json_path")
station_list_path = config.get("METADATA", "station_list_path")
coordinate_output = config.get("METADATA", "coordinate_output")

#[DOWNLOAD]
perform_download = config.getboolean("DOWNLOAD", "perform_download")
token_path = config.get("DOWNLOAD", "token_path")
station_input_path = config.get("DOWNLOAD", "station_list_path")
number_of_cpus = config.getint("DOWNLOAD", "number_of_cpus")
components = config.get("DOWNLOAD", "components").split(',')
channels = config.get("DOWNLOAD", "channels").split(',')
dt = config.getfloat("DOWNLOAD", "dt")
max_gap = config.getfloat("DOWNLOAD", "max_gap")
date_format = config.get("DOWNLOAD", "date_format")
data_percentage = config.getfloat("DOWNLOAD", "data_percentage")
sleep_time =  config.getint("DOWNLOAD", "sleep_time")
attempts = config.getint("DOWNLOAD", "attempts") 
saving_directory = config.get("DOWNLOAD", "saving_directory")
override = config.getboolean("DOWNLOAD", "override")


#[PROCESSING]
processing = config.getboolean("PROCESSING", "processing")
resample = config.getboolean("PROCESSING", "resample")
detrend_option = config.get("PROCESSING", "detrend_option")
sampling_freq = config.getint("PROCESSING", "sampling_freq")
anti_aliasing_filter = config.getfloat("PROCESSING", "anti_aliasing_filter")
filter_order = config.getint("PROCESSING", "filter_order")
zero_phase = config.getboolean("PROCESSING", "zero_phase")
apply_broadband_filter = config.getboolean("PROCESSING", "apply_broadband_filter")
broadband_filter = map(float, config.get("PROCESSING", "broadband_filter").split(","))

#[NORMALIZATION]
timedomain_normalization = config.getboolean("NORMALIZATION", "timedomain_normalization")
filter_num = config.getint("NORMALIZATION", "filters")
filters = []
i = 1
while i <= filter_num:
    f = map(float, config.get("NORMALIZATION", "filter%s" % (i)).split(','))
    filters.append(f)
    i += 1

envsmooth = config.getint("NORMALIZATION", "envsmooth")
env_exp = config.getfloat("NORMALIZATION", "env_exp")
min_weight = config.getfloat("NORMALIZATION", "min_weight")
taper_length_tdn = config.getint("NORMALIZATION", "taper_length_tdn")
plot = config.getboolean("NORMALIZATION", "plot")

#[SPECTRAL-WHITENING]
apply_whitening = config.getboolean("SPECTRAL-WHITENING", "apply_whitening")
spectrumexp = config.getfloat("SPECTRAL-WHITENING", "spectrumexp")
espwhitening = config.getfloat("SPECTRAL-WHITENING", "espwhitening")
taper_length_whitening = config.getint("SPECTRAL-WHITENING", "taper_length_whitening")