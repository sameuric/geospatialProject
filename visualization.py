import json
import os
import webbrowser
from datetime import datetime

import psycopg2
from folium.plugins import TimestampedGeoJson
# gtfs-realtime-bindings
import folium
import osm
from db import retrieveDepartureStation, retrieveArrivalStation, retrieveStations, retrievePath
import osmnx as ox

def retrieveCoordinates(currentMoment):
    """
    Function that allows retrieving coordinates from the travels.txt file and add it into a
    coordinate object, used to create a json object
    :return: the coordinate object
    """
    coordinates = []
    index = 0
    with open('travels.txt', 'r') as travels:
        for i, line in enumerate(travels):
            longitude = float(line.split(',')[1])
            latitude = float(line.split(',')[0])
            epochTime = float(line.split(',')[2])
            try:
                nextEpochTime = float(next(travels).split(',')[2])
            except StopIteration:
                break
            nextLine = travels.readline()
            if nextLine != '':
                if nextEpochTime > currentMoment:
                    coordinates.append({"coordinates": [latitude, longitude],
                                        "time": datetime.fromtimestamp(float(epochTime)).isoformat() + "Z"})
                index += 1
            else:
                coordinates.append({"coordinates": [latitude, longitude],
                                    "time": datetime.fromtimestamp(float(epochTime)).isoformat() + "Z"})
        return coordinates


def testGeoJson():
    feature_collection = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[3.6859148, 50.4101452], [3.6918031, 50.4115532]]
            },
            "properties": {
                "times": ['2023-03-27T21:02:00Z', '2023-03-27T21:04:00Z']
            }
        }]
    }
    return [feature_collection]


def truncateCoordinates(currentMoment, coordinates):
    # 1679955725
    #print(coordinates)
    #print(currentMoment)
    pass


def createGeoJSON(currentMoment):
    """
    Function that creates a geoJSON object. We pass it coordinates so the pin on the map can move
    according to a determined time
    :return:
    """
    coordinates = retrieveCoordinates(currentMoment)
    truncateCoordinates(currentMoment, coordinates)

    # for coordinates in coordinatesSet:
    #    coordinates[0]['coordinates'] = coordinates[1]['coordinates']
    geoJSONSet = []

    feature_collection = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [coord["coordinates"] for coord in coordinates]
            },
            "properties": {
                "times": [coord["time"] for coord in coordinates]
            }
        }]
    }
    geoJSONSet.append(feature_collection.copy())
    return geoJSONSet


def visualizeTrains(currentMoment):
    """
    Function that allows visualizing moving trains on a map. First we create a map and center it
    on a set of coordinates. Then, we create a geoJSOn object, define its parameters, save it into
    and html file and open the html
    :return:
    """
    belgium_coords = [51.17147, 4.142963]
    m = folium.Map(location=belgium_coords, zoom_start=10)

    feature_collection = createGeoJSON(currentMoment)

    # Add the GeoJSON data to the map

    # create TimestampedGeoJson object for the current feature collection
    geojson = TimestampedGeoJson(
        json.dumps(feature_collection),
        period="PT1S",  # update frequency in seconds
        add_last_point=True,  # add a marker at the last point of the trajectory
        auto_play=True,  # autoplay the animation
        loop=True,  # loop the animation
    )

    # add the TimestampedGeoJson object to the map

    geojson.add_to(m)

    # Show the map in PyCharm
    m.save("map.html")
    travelPath = 'travels.txt'
    if os.path.exists(travelPath):
        os.remove(travelPath)
    return "map.html"
    #webbrowser.open('map.html')


def retrieveInDb(station1, station2, epoch):
    conn = psycopg2.connect(database="traindb", user="postgres", password="password", host="localhost", port="5432")
    departureStation = retrieveDepartureStation(conn, station1, epoch)
    arrivalStation = retrieveArrivalStation(conn, station2, epoch)

    # on peut simplifier, je laisse comme ça pour le débeug
    validArrivalStation, validDepartureStation = retrieveStations(arrivalStation, departureStation)
    if len(validArrivalStation) == 0 or len(validDepartureStation) == 0:
        return []
    if validDepartureStation[0][0][-1] == validArrivalStation[0][-1]:#-1
        tripId = validArrivalStation[0][-2] #-1
        trip = retrievePath(conn, tripId)
        conn.close()
        return trip


class gtfsData:
    def __init__(self, osmdata, travel):
        trip = retrieveInDb(travel[0], travel[1], travel[2])
        if len(trip) == 0:
            self.found = False
        else:
            self.found = True
            startTime = trip[0][4]
            endTime = trip[-1][4]
            osm.retrieveTripCoordinates(startTime, trip, osmdata)
            self.file = visualizeTrains(travel[2])
