import psycopg2
import os
import common

"""
sudo -u postgres psql
CREATE USER geoProject WITH PASSWORD 'geoProject';
CREATE USER geoDataProject WITH PASSWORD 'password';

CREATE DATABASE traindb;
GRANT ALL PRIVILEGES ON DATABASE traindb TO geoProject;
"""

def main():
    con, cur = connectToDB()
    #createTable(cur)
    #importGtfsData(cur)
    #printTable(con, cur)
    cur.close()
    con.close()


def connectToDB():
    conn = psycopg2.connect(database="traindb", user="postgres", password="password", host="localhost", port="5432")
    cur = conn.cursor()
    return conn, cur


def createTable(cur):
    cur.execute("DROP TABLE IF EXISTS station;")
    cur.execute('''CREATE TABLE station
               (id SERIAL PRIMARY KEY,
                nameStation TEXT,
                latStation FLOAT,
                longStation FLOAT,
                arrivalTime INT,
                trip INT,
                delay INT);''')


def insertInTable(cur, data):
    cur.execute("INSERT INTO station (nameStation, latStation, longStation, arrivalTime, trip, delay) VALUES (%s, %s, %s, "
                "%s, %s, %s)",
                (data[0][0], float(data[0][1]), float(data[0][2]), int(data[1]), data[2], int(data[3])))


def printTable(conn, cur):
    cur.execute("SELECT * FROM station")
    conn.commit()
    rows = cur.fetchall()
    for row in rows:
        print(row)


def loadGtfsData(cur, url, counter):
    positionsDict = common.findStationPositions()
    gtfsDict = common.preprocessing(url)
    if gtfsDict:
        if len(gtfsDict) == 2:
            gtfsValues = list(gtfsDict.values())[1]
            if gtfsValues:
                for i in range(len(gtfsValues)):
                    res = findStations(gtfsValues, positionsDict, i, counter)
                    if res:
                        print(counter)
                        counter += 1
                        for station in res:
                            insertInTable(cur, station)
    return counter


def importGtfsData(cur):
    dataPath = "data/"
    files = os.listdir(dataPath)
    #todo : make for all the gtfsrt files
    files = [files[0], files[1]]
    counter = 0
    for file in files:
        cwd = os.getcwd()
        full_path = os.path.join(cwd, dataPath+file)
        url = 'file://' + full_path
        if url.endswith(".gtfsrt"):
            counter = loadGtfsData(cur, url, counter)


def findStations(gtfsValues, positionsDict, trip, counter):
    res = []
    stops = gtfsValues[trip]['tripUpdate']['stopTimeUpdate']
    if len(stops) > 1:
        for i in range(len(stops)):
            if i == len(stops)-1:
                res.append([positionsDict[stops[i]['stopId']],
                            stops[i]['arrival']['time'], counter, 0])

            else:
                if 'departure' not in stops[i] and i > 0:
                    stops[i]['departure'] = {'delay': stops[i - 1]['departure']['delay'],
                                             'time': stops[i - 1]['departure']['time']}
                if 'departure' in stops[i]:
                    res.append([positionsDict[stops[i]['stopId']],
                                stops[i]['departure']['time'], counter, stops[i]['departure']['delay']])

        return res


#main()


def retrievePath(conn, trip):
    cur = conn.cursor()
    cur.execute("select * from station where trip = %s order by arrivalTime", (trip,))
    conn.commit()
    rows = cur.fetchall()
    cur.close()
    return rows


def retrieveStations(arrivalStation, departureStation):
    stationDico = {}
    for station in departureStation:
        keyTrip = station[-1]
        if keyTrip in stationDico:
            stationDico[keyTrip].append(station)
        else:
            stationDico[keyTrip] = [station]
    validDepartureStation = []
    validArrivalStation = []
    for station in arrivalStation:
        keyTrip = station[-1]
        if keyTrip in stationDico:
            validDepartureStation.append(stationDico[keyTrip])
            validArrivalStation.append(station)
    return validArrivalStation, validDepartureStation


def retrieveArrivalStation(conn, station, epoch):
    cur = conn.cursor()
    cur.execute("select * from station where nameStation = %s and arrivalTime > %s", (station, epoch,))
    conn.commit()
    rows = cur.fetchall()
    cur.close()
    return rows


def retrieveDepartureStation(conn, station, epoch):
    cur = conn.cursor()
    cur.execute("select * from station where nameStation = %s and arrivalTime < %s", (station, epoch,))
    conn.commit()
    rows = cur.fetchall()
    cur.close()
    return rows


main()
