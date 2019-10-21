from classes import metadata
import obspy
if __name__ == "__main__":
    print "obspy version:",obspy.core.util.version.read_release_version()
    metadata = metadata.Metadata(
        lat = 45,
        lon = 19,
        radius = 8,
        start_year = obspy.core.UTCDateTime(2017,1,1),
        end_year = obspy.core.UTCDateTime(2018,1,1),
        token_path = "./eidatoken"
    )
    metadata.save_inventory(
        save_path = "./metadata_NIEP.xml"
    )
    #metadata.read_inv(
    #    load_path = "./metadata.xml"
    #)

    inventory = metadata.get_inventory()
    print inventory
    """for network in inventory:
        print network
        for station in network:
            print station
    """
