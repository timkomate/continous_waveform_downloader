import multiprocessing
from classes import downloader, metadata

class Download_driver(object):
    def __init__(self, config, filenames):
        self._config = config
        self._filenames = filenames

    def __call__(self, filename):
        self.go(filename)

    def make_metadata(self):
        if (self._config.getboolean("METADATA", "download_metadata")):
            print "Accessign metadata information..."
            metadata = metadata.Metadata(
                lat = self._config.getfloat("METADATA", "latitude"),
                lon = self._config.getfloat("METADATA", "longitude"),
                max_radius = self._config.getfloat("METADATA", "max_radius"),
                start_year = self._config.get("METADATA", "start_year"),
                end_year = self._config.get("METADATA", "end_year"),
            )
            metadata.save_json(save_path = self._config.get("METADATA", "json_path"))
            metadata.make_inputfile(save_path = self._config.get("METADATA", "station_list_path"))
            metadata.extract_station_coordinates(save_path = self._config.get("METADATA", "coordinate_output"))
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
        dw.add_token(token = self._config.get("DOWNLOAD", "token_path"))
        dw.start_download(
            dt = self._config.getint("DOWNLOAD", "dt"),
            components = self._config.get("DOWNLOAD", "components").split(','),
            channels = self._config.get("DOWNLOAD", "channels").split(',')
        )