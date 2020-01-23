from obspy.clients.fdsn import RoutingClient, Client
import obspy
#from setup_logger import logger
import json

class Metadata(object):
    def __init__(self, lat, lon, max_radius, start_year, end_year,
        channel = "*H*", network = "*", level = "station",
        EIDA_nodes = [ "ODC", "GFZ", "RESIF", "INGV", "ETH", "BGR", "NIEP", "KOERI", "LMU", "NOA", "IRIS" ]
        ):
        self._station_dictionary = {}
        self._output_text = []
        self._start_year = obspy.core.UTCDateTime(start_year)
        self._end_year = obspy.core.UTCDateTime(end_year)
        print "Generating metadata..."
        for node in EIDA_nodes:
            print node
            client = obspy.clients.fdsn.Client(node)
            inv = client.get_stations(
                network = network,
                channel = channel,
                starttime = start_year,
                endtime = end_year,
                latitude = lat, 
                longitude = lon,
                level = level,
                maxradius = max_radius
            )
            self.append_dictionary(inv, node)

    def append_dictionary(self, inv, service):
        start_year_string = "%s-%s-%s" % (self._start_year.year, self._start_year.month, self._start_year.day)
        end_year_string = "%s-%s-%s" % (self._end_year.year, self._end_year.month, self._end_year.day)
        for network in inv:
            #print network.code
            if network.code not in self._station_dictionary:
                self._station_dictionary[network.code] = {}
            for station in network:
                start_op, end_op = Metadata.operation_time(station, self._start_year, self._end_year)
                if (station.code not in self._station_dictionary[network.code]):
                    self._station_dictionary[network.code][station.code] = {
                        "latitude" : station.latitude,
                        "longitude" : station.longitude,
                        "elevation" : station.elevation,
                        "start_date" : [str(start_op)],
                        "end_date" : [str(end_op)],
                        "status" : station.restricted_status,
                        "services" : [service]
                    }
                    #self._output_text.append("%s %s %s %s" % (network.code, station.code, start_year_string, end_year_string))
                elif (service not in self._station_dictionary[network.code][station.code]["services"]):
                    self._station_dictionary[network.code][station.code]["services"].append(service)
                else:
                    self._station_dictionary[network.code][station.code]["start_date"].append(str(start_op))
                    self._station_dictionary[network.code][station.code]["end_date"].append(str(end_op))
        

    def save_json(self, save_path):
        with open(save_path, 'w') as fp:
            json.dump(self._station_dictionary, fp, sort_keys=False, indent=2)

    def make_inputfile(self, save_path):
        output = open(save_path,'w')
        for network in self._station_dictionary:
            for station in self._station_dictionary[network]:
                print station
                c = len(self._station_dictionary[network][station]["start_date"])
                for i in range(c):
                    output.write("%s %s %s %s %s\n" % (
                        self._station_dictionary[network][station]["services"][0], 
                        network, 
                        station, 
                        self._station_dictionary[network][station]["start_date"][i],
                        self._station_dictionary[network][station]["end_date"][i]
                        )  
                )
    
    def extract_station_coordinates(self, save_path):
        output = open(save_path,'w')
        for network in self._station_dictionary:
            for station in self._station_dictionary[network]:
                output.write("%s %s %s %s\n" % (
                    self._station_dictionary[network][station]["longitude"], 
                    self._station_dictionary[network][station]["latitude"],
                    self._station_dictionary[network][station]["elevation"],
                    station
                    )  
                )

    def save_inventory(self, save_path, format = "STATIONXML"):
        self._inv.write(
            path_or_file_object = save_path,
            format = format
        )  
    
    def read_inv(self, load_path):
        self._inv = obspy.read_inventory(load_path)

    def get_inventory(self):
        return self._inv

    @staticmethod
    def operation_time(sta,t_start, t_end, output_format = "%Y-%m-%d"):
        station_start = sta.start_date
        station_end = sta.end_date
        if t_start < station_start:
            op_start = station_start
        else:
            op_start = t_start
        if station_end == None:
            op_end = t_end
        elif t_end < station_end:
            op_end = t_end
        else:
            op_end = station_end
        return [op_start.strftime(output_format), op_end.strftime(output_format)]

    

