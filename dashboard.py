import os
import webbrowser

from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from dateutil.parser import parse
from PyQt5.QtWidgets import QComboBox, QDateEdit, QApplication, QWidget, QPushButton, \
    QVBoxLayout, QLabel, QLineEdit, QTabWidget, QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy, \
    QMessageBox, QMainWindow, QTextBrowser, QPlainTextEdit
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QDate, Qt, QUrl
from datetime import datetime
import osmnx as ox
import visualization
from db import retrieveStations


class Fenetre(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        graphPath = 'railwayGraph.graphml'
        if os.path.exists(graphPath):
            G = ox.load_graphml(graphPath)
        else:
            place_name = "Belgium"
            G = ox.graph_from_place(place_name, custom_filter='["railway"]')
            ox.save_graphml(G, graphPath)
        self.osmdata = G

        self.initWindow()

        self.page2 = self.createTabs()

        self.setpage(self.page2)

        # Add tabs to main window
        self.setTabs(self.page2)

    def setTabs(self, page2):
        self.qtw = QTabWidget(self)
        self.qtw.addTab(page2, "Trip details")
        # Stylize the main window
        self.setMinimumWidth(1000)
        self.setMinimumHeight(800)
        # Stylize the sub-pages
        self.qtw.setMinimumWidth(1000)
        self.qtw.setMinimumHeight(750)
        self.qtw.move(60, 60)
        self.setWindowTitle("Dashboard")

    def setpage(self, page2):
        # Ajout des labels
        self.setLabels(page2)
        # table to contain the list of trips
        station_names = set()
        # collecting trips from the gtfs file
        self.departure, self.destination = self.setScrollBox(page2, station_names)
        self.setTime(page2)
        # Add list of stationstationList
        self.setStationsList(page2)
        # Sub-layouts
        self.setLayouts(self.departure, self.destination, page2)

    def setLayouts(self, departure, destination, page2):
        """
        Add components to their respective layout
             slayout1   A sub-layout used to display horizontally
             slayout2   A sub-layout for the date input
             layout2    Main layout
        """
        slayout1 = QHBoxLayout()
        slayout1.addWidget(page2.lab1, Qt.AlignLeft)
        slayout1.addWidget(page2.hours)
        slayout1.addWidget(page2.lab2)
        slayout1.addWidget(page2.minutes)
        # slayout1.setContentsMargins(0, 0, 0, 0)
        # slayout1.setSpacing(0)
        # Date sub-layout
        slayout2 = QHBoxLayout()
        slayout2.addWidget(page2.lab5, Qt.AlignLeft)
        slayout2.addWidget(page2.date)
        slayout1.setContentsMargins(0, 0, 0, 0)
        # slayout1.setSpacing(0)
        # Layouts
        layout1 = QVBoxLayout()
        # Layout page 2
        layout2 = QGridLayout()
        layout2.addWidget(page2.lab0, 0, 0)
        layout2.addLayout(slayout2, 1, 0)
        layout2.addLayout(slayout1, 2, 0)
        layout2.addWidget(page2.lab3, 3, 0)
        layout2.addWidget(departure, 4, 0)
        layout2.addWidget(page2.lab4, 5, 0)
        layout2.addWidget(destination, 6, 0)
        layout2.addWidget(page2.search, 7, 0)
        layout2.addWidget(page2.mean, 8, 0)
        layout2.addWidget(page2.stationList, 9, 0)
        verticalSpacer = QSpacerItem(40, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout2.addItem(verticalSpacer, 7, 0, Qt.AlignTop)
        page2.setLayout(layout2)

    def setTime(self, page2):
        # Edition de l'heure
        page2.hours = QLineEdit("13")
        page2.minutes = QLineEdit("24")
        # Edition de la date
        page2.date = QDateEdit()
        page2.date.setDisplayFormat("dd-MM-yyyy")
        #page2.date.setDate(QDate.currentDate())
        page2.date.setDate(QDate(2023, 3, 21))
        page2.date.setStyleSheet("QDateEdit {padding: 3px; margin: 10px; width:110px}")

    

    def setScrollBox(self, page2, station_names):
        with open('data/gtfs/stops.txt', 'r') as file:
            trips = file.readlines()[1:]
        # Ajout de la sélection du départ et destination
        departure = QComboBox(page2)
        destination = QComboBox(page2)
        
        # Retrieving all stops in the file
        sortedList = []
        for line in trips:
            trip_list = line.split(',')
            trip = trip_list[2].split(' ')[0]
            if trip not in station_names:
                sortedList.append(trip)
        
        # Remove redondancy and sort station's list
        sortedList = sorted(list(set(sortedList)))
        
        for trip in sortedList:
            station_names.add(trip)
            destination.addItem(trip)
            departure.addItem(trip)
        return departure, destination

    def setLabels(self, page2):
        page2.lab0 = QLabel("My travel")
        page2.lab0.setStyleSheet("QLabel { font: 15pt; font-family:'Cambria'; margin: 10px 0 20px 160px }")
        page2.lab1 = QLabel("Time:")
        page2.lab2 = QLabel(":")
        page2.lab3 = QLabel("From:")
        page2.lab4 = QLabel("To:")
        page2.lab5 = QLabel("Date:")

    def createTabs(self):
        # Create tab pages
        page2 = QWidget()
        page2.setStyleSheet("QLabel {margin-top: 10px}")
        self.setStyleSheet("QLineEdit {max-width:30px; padding: 3px}")
        page2.setStyleSheet("QComboBox {margin-bottom: 10px; padding: 5px}")
        page2.search = QPushButton("Search")
        page2.search.clicked.connect(self.retrieveTrip)
        page2.search.setStyleSheet("QPushButton {margin-bottom:10px;padding:5px;text-align:center}")
        page2.mean = QPushButton("Average delay for this line")
        page2.mean.clicked.connect(self.showMeanDelay)
        page2.mean.setStyleSheet("QPushButton {margin-bottom:25px;padding:5px;}")
        page2.mean.setFixedWidth(300)
        page2.search.setFixedWidth(300)
        return page2

    def initWindow(self):
        # Background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#cccccc'))
        self.setPalette(palette)
    
    
    def showMeanDelay(self):
        """
        Display on the interface the average delay for each station
        on a selected trip
        """
    
        # Define time limits for the actual day
        today = parse(self.page2.date.date().toString())
        epochMorning = int(datetime(today.year, today.month, today.day, 0, 0).timestamp())
        epochEvening = int(datetime(today.year, today.month, today.day, 23, 59).timestamp())
        
        # Search the trip
        departureStation = self.departure.currentText()
        arrivalStation = self.destination.currentText()
        
        if departureStation == arrivalStation:
            self.showInvalidTrip()
            return
        
        means = visualization.meanDelays(departureStation, arrivalStation, self.retrieveTime(), epochMorning, epochEvening)
        
        #print("------ Mean Delay -------")
        #print(means)
        
        # Clear list before printing new one
        self.page2.stationList.clear()
        self.page2.stationList.appendPlainText("[STATION]".ljust(20) + "   " + "[MEAN DELAY]")
        
        for row in means:
            self.page2.stationList.appendPlainText(row[0].ljust(20) + "       " + str(row[1]) + " min")
        
        
        
    def retrieveTime(self):
        hours = int(self.page2.hours.text()) # we do -2 because we live in gmt +2
        minutes = int(self.page2.minutes.text())
        date = self.page2.date.date().toString()
        dateObj = parse(date)

        time = datetime(dateObj.year, dateObj.month, dateObj.day, hours, minutes)
        epochTime = time.timestamp()
        return int(epochTime)
        
        
    def showStationsList(self, departureStation, arrivalStation):
        """
        Show a list of all stations between arrival and departure,
        alongside with their arrival time and time delay
        """
        stationList = visualization.retrieveInDb(departureStation, arrivalStation, self.retrieveTime())
        
        #print("------ Station List -------")
        #print(stationList)
       
        # We don't need stations out of selected inputs
        relevantStations = []
        relevant = False
        for station in stationList:
            if station[1] == arrivalStation or station[1] == departureStation:
                if self.retrieveTime() < int(station[4]):
                    relevantStations.append(station)
                relevant = not relevant
            elif relevant:
                if self.retrieveTime() < int(station[4]):
                    relevantStations.append(station)
        
        
        #print("------ Relevant station list -------")
        #print(relevantStations)
        
        
        # Clear list before printing new one
        self.page2.stationList.clear()
        self.page2.stationList.appendPlainText("[STATION]".ljust(20) + "   " + "[TIME]" +  "     " + "[DELAY]")
        
        for station in relevantStations:
            arrTime = station[4] - station[6]
            arrTime = datetime.fromtimestamp(float(arrTime)).strftime("%H:%M")
            delay = int(station[6]/60)
            self.page2.stationList.appendPlainText(station[1].ljust(20) + "   " + arrTime + "      +" + str(delay).ljust(2) + "min")




    def retrieveTrip(self):
        time = self.retrieveTime()
        departureStation = self.departure.currentText()
        arrivalStation = self.destination.currentText()
        
        if departureStation == arrivalStation:
            self.showInvalidTrip()
            return
        else:
            data = visualization.gtfsData(self.osmdata, [departureStation, arrivalStation, time])
            if data.found:
                file_ = data.file
                webbrowser.open(data.file)
            else:
                self.showNoTripFound()
    
        self.showStationsList(departureStation, arrivalStation)
        
        
    
    
    def setStationsList(self, page2):
        """
        Create and display a list of stations
        as a QPlainTextEdit widget on the board
        """
        page2.stationList = QPlainTextEdit()
        page2.stationList.setReadOnly(True)
        #page2.stationList.setEnabled(False)
        page2.stationList.setFixedHeight(200)
        page2.stationList.setStyleSheet("QPlainTextEdit {color:#4400AA;font-family:monospace;}")
        
        
    def showNoTripFound(self):
        message_box = QMessageBox()
        message_box.setText("No trip found.")
        message_box.setWindowTitle("Invalid travel")
        message_box.setIcon(QMessageBox.Information)
        message_box.setStandardButtons(QMessageBox.Ok)
        result = message_box.exec_()

    def showInvalidTrip(self):
        message_box = QMessageBox()
        message_box.setText("Departure station cannot be the same as arrival station.")
        message_box.setWindowTitle("Invalid travel")
        message_box.setIcon(QMessageBox.Information)
        message_box.setStandardButtons(QMessageBox.Ok)
        result = message_box.exec_()

    


app = QApplication.instance()
if not app:
    app = QApplication([])

fen = Fenetre()
fen.show()

app.exec_()
