from classes import metadata, downloader, download_driver
import obspy
import os, glob
import ConfigParser


if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("./config.cfg")

    print "obspy version:",obspy.core.util.version.read_release_version()
    
    if (config.getboolean("METADATA", "download_metadata")):
        metadata = metadata.Metadata(
            lat = config.getfloat("METADATA", "latitude"),
            lon = config.getfloat("METADATA", "longitude"),
            max_radius = config.getfloat("METADATA", "max_radius"),
            start_year = config.get("METADATA", "start_year"),
            end_year = config.get("METADATA", "end_year"),
        )
        metadata.save_json(save_path = config.get("METADATA", "json_path"))
        metadata.make_inputfile(save_path = config.get("METADATA", "station_list_path"))
        metadata.extract_station_coordinates(save_path =config.get("METADATA", "coordinate_output"))

    input_path = config.get("DOWNLOAD", "station_list_path")
    input_list = [f for f in glob.glob("%s/*.text*" % (input_path))]
    input_list = sorted(input_list)
    dw_d = download_driver.Download_driver(config, input_list)
    dw_d.start(core_number = config.getint("DOWNLOAD", "number_of_cpus"))