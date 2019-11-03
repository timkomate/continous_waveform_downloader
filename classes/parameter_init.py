import ConfigParser

config = ConfigParser.ConfigParser()
config.read("./config.cfg")

#[METADATA]
download_metadata = config.getboolean("METADATA", "download_metadata")
latitude = config.getfloat("METADATA", "latitude")
longitude = config.getfloat("METADATA", "longitude")
max_radius = config.getfloat("METADATA", "max_radius")
start_year = config.get("METADATA", "start_year")
end_year = config.get("METADATA", "end_year")
json_path = config.get("METADATA", "json_path")
station_list_path = config.get("METADATA", "station_list_path")
coordinate_output = config.get("METADATA", "coordinate_output")

#[DOWNLOAD]
token_path = config.get("DOWNLOAD", "token_path")
station_input_path = config.get("DOWNLOAD", "station_list_path")
number_of_cpus = config.getint("DOWNLOAD", "number_of_cpus")
components = config.get("DOWNLOAD", "components").split(',')
channels = config.get("DOWNLOAD", "channels").split(',')
dt = config.getfloat("DOWNLOAD", "dt")
max_gap = config.getfloat("DOWNLOAD", "max_gap")
data_percentage = config.getfloat("DOWNLOAD", "data_percentage")
sleep_time =  config.getint("DOWNLOAD", "sleep_time")
attempts = config.getint("DOWNLOAD", "attempts") 
saving_directory = config.get("DOWNLOAD", "saving_directory")
override = config.getboolean("DOWNLOAD", "override")


#[PROCESSING]
processing = config.getboolean("PROCESSING", "processing")
timedomain_normalization = config.getboolean("PROCESSING", "timedomain_normalization")
merge_option = config.get("DOWNLOAD", "merge_option")
detrend_option = config.get("DOWNLOAD", "detrend_option")
sampling_freq = config.getint("DOWNLOAD", "sampling_freq")
bandpass_freqmin = config.getfloat("DOWNLOAD", "bandpass_freqmin")
bandpass_freqmax = config.getfloat("DOWNLOAD", "bandpass_freqmax")