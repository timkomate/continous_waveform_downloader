from classes import metadata, downloader, download_driver, parameter_init
import obspy
import os, glob
import ConfigParser


if __name__ == "__main__":
    #print parameter_init.perform_download

    print "obspy version:",obspy.core.util.version.read_release_version()
    
    if (parameter_init.download_metadata):
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
    
    if (parameter_init.perform_download):
        input_path = parameter_init.station_input_path
        input_list = [f for f in glob.glob("%s/*.text*" % (input_path))]
        input_list = sorted(input_list)
        print input_list
        dw_d = download_driver.Download_driver(input_list)
        dw_d.start(core_number = parameter_init.number_of_cpus)

#TODO
#Does the 10^-9 factor really necessarily?
#Whitening is slow, probably due to the len of my data vector. Could be solved by next2pow.
#partly solved but needs to check