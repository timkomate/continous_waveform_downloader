from classes import metadata
from classes import downloader
import obspy
import ConfigParser


if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("./config.cfg")

    print "obspy version:",obspy.core.util.version.read_release_version()
    if (config.getboolean("DEFAULT", "download_metadata")):
        metadata = metadata.Metadata(
            lat = config.getfloat("DEFAULT", "latitude"),
            lon = config.getfloat("DEFAULT", "longitude"),
            max_radius = config.getfloat("DEFAULT", "max_radius"),
            start_year = config.get("DEFAULT", "start_year"),
            end_year = config.get("DEFAULT", "end_year"),
        )
        metadata.save_json("./stations.json")
        metadata.make_inputfile("./input.text")
        metadata.extract_station_coordinates("./coordinates.xy")

    dw = downloader.Downloader("./input.text")
    dw.add_token("./eidatoken")
    #dw.add_clients([ "ODC", "GFZ", "RESIF", "INGV", "ETH", "BGR", "NIEP", "KOERI", "LMU", "NOA", "IRIS" ])
    dw.add_clients([ "ODC", "GFZ" ])
    dw.start_download()