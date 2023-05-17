import itertools
import osmnx as ox
from geopy.distance import distance


def extrapolate(routeNodes, start, end):
    """
    Function that checks if the distance beteen 2 stations is greater than 250m. If so, adds a point 'mid' in the path
     between the departure and destination station, at 250m of the departure station,and this 'recursively' with the
     'mid' point, which becomes the start point.
    :param routeNodes: path that the train follows
    :param start: departure station
    :param end: arrival station
    :return:
    """
    length = distance(start, end).meters
    while length > 250:
        mid = getMid(end, length, start)
        routeNodes.insert(routeNodes.index(end), mid)
        start = mid
        length = distance(start, end)


def getMid(end, length, start):
    """
    Function that finds the coordinates of a point at 250m
    :param end:
    :param length:
    :param start:
    :return:
    """
    point_ratio = 250 / length
    point_lat = start[0] + point_ratio * (end[0] - start[0])
    point_lon = start[1] + point_ratio * (end[1] - start[1])
    return point_lat, point_lon


def retrieveTripCoordinates(startTime, trip, G):
    """
    Function that retrieves trip coordinates in function of a start time, list of stations and coordinates, and an OSM
    graph
    :param startTime: start time of the trip
    :param trip: list of tuples (station , (coordinates) )
    :param G: OSM data containing the whole Infrabel network
    :return:
    """
    for i in range(len(trip) - 1):
        routeNodes = extractCoordinates(G, trip[i], trip[i + 1])
        startTime = writeInFile(routeNodes, startTime, trip[i], trip[i + 1])


def extractCoordinates(G, station1, station2):
    """
    Function that retrieves the OSM data of a departure station and an arrival station. With this OSM data, calculates
    the shortest path on the Belgian Railway between the 2 stations and gives a set of coordinates for this path. Then,
    extrapolate between all the coordinates of the path.
    :param G: The OSM data to retrieve the stations on
    :param station1: coordinates of the departure station
    :param station2: coordinates of the arrival station
    :return: the lsit of coordinates of the path
    """
    station1 = ox.nearest_nodes(G, float(station1[3]), float(station1[2]))
    station2 = ox.nearest_nodes(G, float(station2[3]), float(station2[2]))
    route = ox.shortest_path(G, station1, station2)
    routeNodes = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
    routeNodes = [key for key, group in itertools.groupby(routeNodes)]
    distances = 0
    if len(routeNodes) > 1:
        i = 0
        while i < len(routeNodes) - 1:
            distances += distance([routeNodes[i][0], routeNodes[i][1]],
                                  [routeNodes[i + 1][0], routeNodes[i + 1][1]]).m
            extrapolate(routeNodes, routeNodes[i], routeNodes[i + 1])
            i += 1

    return routeNodes


def writeInFile(routeNodes, startTime, station1, station2):
    """
    Function that writes in a file the set of coordinates and their corresponding time, to add them later into a
    geoJSON object
    :param routeNodes: list of coordinates (between stations) to write in the geoJSON object
    :param startTime: start time of the trip
    :param station1: departure station
    :param station2: arrival station
    :return:
    """
    tripTime = station2[4] - station1[4]
    for i in range(len(routeNodes)):
        totalTime = tripTime / len(routeNodes)
        startTime += totalTime
        with open('travels.txt', 'a+') as travels:
            travels.write(f"{routeNodes[i][1]},{routeNodes[i][0]},{int(startTime)}\n")
            travels.close()

    return startTime
