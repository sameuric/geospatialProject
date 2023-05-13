from urllib.request import urlopen

from google.protobuf.json_format import MessageToDict
from google.transit import gtfs_realtime_pb2


def findStationPositions():
    """
    Opens the gtfs/stops.txt and retrieves each line. In each line, we retrieve the information of
    the station, based on the stopID.
    IMPORTANT: please change the path to the location of your gtfs/stops.txt file
    :return: the dictionary containing the stopID as the key and the rest of infos as values.
    """
    # path = "C:/Users/maeva/Desktop/geo/gtfs/stops.txt"
    path = "data/gtfs/stops.txt"

    valuesSeen = set()
    positionsDict = {}
    with open(path, 'r') as f:
        for line in f:
            stopId = line.split(',')[0]

            if '_' in stopId:
                stopId = stopId.split('_')[0]
            if stopId not in valuesSeen and stopId.isdigit():
                valuesSeen.add(stopId)
                addLocations(stopId, line, positionsDict)
    return positionsDict


def preprocessing(url):
    """
    Allows to retrieve the gtfsrt file content and put it into a dictionary
    :param url: path of the file under the url format
    :return: the dictionary object
    """
    gtfs_realtime = gtfs_realtime_pb2.FeedMessage()
    gtfs_realtime.ParseFromString(urlopen(url).read())
    dict_obj = MessageToDict(gtfs_realtime)
    return dict_obj


def addLocations(stopId, line, positionsDict):
    """
    Function that allows retrieving the name, longitude and latitude of a station based on its ID
    :param stopId: ID of the station
    :param line: line of the file "stops.txt", where all the information about stations are written
    :param positionsDict: dictionary to which is appended the new location, longitude and latitude
    as values, and the stopID as key
    :return: dictionary mentioned earlier
    """

    location = line.split(',')[2]
    longitude = line.split(',')[4]
    lattitude = line.split(',')[5]

    positionsDict[stopId] = [location, longitude, lattitude]
