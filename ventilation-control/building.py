#!/usr/local/bin/python
# coding: utf-8

import ConfigParser
import sys

sys.path.insert(0, '../lnetatmo')
import lnetatmo

class Sensor:
    def getHumidity(self):
        raise NotImplementedError( "Should have implemented this" )
    def getTemperature(self):
        raise NotImplementedError( "Should have implemented this" )

class NetatmoSensor(Sensor):
    def __init__(self, netatmoName):
        self.netatmoName = netatmoName
        self.natatmoAuthorization = None

    def getNetatmoDevList(self):
        netatmoDevList = None

        if self.natatmoAuthorization == None:
            config = ConfigParser.ConfigParser()
            config.read("netatmo-auth.cfg")

            if config.get("Netatmo_Auth", "clientsecret") == "":
                raise RuntimeError('Netatmo authentication information are missing in netatmo-auth.cfg')

            self.natatmoAuthorization = lnetatmo.ClientAuth( clientId = config.get("Netatmo_Auth", "clientid"),
                                                             clientSecret = config.get("Netatmo_Auth", "clientsecret"),
                                                             username = config.get("Netatmo_Auth", "username"),
                                                             password = config.get("Netatmo_Auth", "password") )

            if self.natatmoAuthorization == None:
                raise RuntimeError('Netatmo authentication failed')
        
        netatmoDevList = lnetatmo.DeviceList(self.natatmoAuthorization)

        if netatmoDevList == None:
            raise RuntimeError('Could not get Netatmo device list')

        return netatmoDevList

    def getHumidity(self):
        #print("Trying to get Humidity from %s" % self.netatmoName)
        return self.getNetatmoDevList().lastData()[self.netatmoName]['Humidity']

    def getTemperature(self):
        #print("Trying to get Temperature from %s" % self.netatmoName)
        return self.getNetatmoDevList().lastData()[self.netatmoName]['Temperature']

class DemoSensor(Sensor):
    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity

    def getHumidity(self):
        #print("DEMO: getHumidity() %s" % self.humidity)
        return self.humidity

    def getTemperature(self):
        #print("DEMO: getTemperature() %s" % self.temperature)
        return self.temperature

class Actor:
    name = "Actor-with-no-name"

    def setPowerOn(self, on):
        raise NotImplementedError( "Should have implemented this" )

    def is_on(self):
        raise NotImplementedError( "Should have implemented this" )        

class DemoActor(Actor):
    def setPowerOn(self, on):
        print( "Switching actor %s to %r" % (self.name, on) )

    def is_on(self):
        return True


class Room:
    name = "Room-with-no-name"
    insideSensor = None
    outsideSensor = None
    actor = None
    minInsideTemp = 0.0
    minHumidDiff = 0.0
    ventilationDuration = 0.0

    def __str__(self):
        return "Room: " + self.name + "\n" + \
            "  Temperature(in/out): " + \
            str(self.insideSensor.getTemperature()) + " / " + \
            str(self.outsideSensor.getTemperature()) + \
            "\n" + \
            "  Humidity(in/out): " + \
            str(self.insideSensor.getHumidity()) + " / " + \
            str(self.outsideSensor.getHumidity()) + \
            "\n" + \
            "  Minimum inside temperatur: " + str(self.minInsideTemp) + \
            "\n" + \
            "  Minimum Humidity difference: " + str(self.minHumidDiff)


def getSensorByName(config, sensorName):
    sensorType = config.get(sensorName, "Type")

    sensor = None

    if sensorType == "Netatmo":
        netatmoName = config.get(sensorName, "NetatmoName")
        sensor = NetatmoSensor(netatmoName)
    elif sensorType == "Demo":
        temperature = config.getfloat(sensorName, "Temperature")
        humidity = config.getfloat(sensorName, "Humidity")
        sensor = DemoSensor(temperature, humidity)

    return sensor

def getActorByName(config, actorName):
    actorType = config.get(actorName, "Type")

    actor = None

    if actorType == "Demo":
        actor = DemoActor()
        actor.name = actorName

    return actor

def createRoom(config, roomName):
    section = "Room_" + roomName
    insideSensorName = config.get(section, "InsideSensor")
    outsideSensorName = config.get(section, "OutsideSensor")
    actorName = config.get(section, "Actor")

    room = Room()
    room.name = roomName
    room.insideSensor = getSensorByName(config, insideSensorName)
    room.outsideSensor = getSensorByName(config, outsideSensorName)
    room.actor = getActorByName(config, actorName)
    room.minInsideTemp = config.getfloat(section, "MinimumInsideTemperaturInDegreeCentigrade")
    room.minHumidDiff = config.getfloat(section, "MinimumHumidityDifference")
    room.ventilationDuration = config.getfloat(section, "VentilationDurationInMinutes")

    return room


def getRooms():
    config = ConfigParser.ConfigParser()
    config.read("ventilation.cfg")

    rooms = []
    
    # create every configured room with its sensors
    sections = config.sections()
    for section in sections:
        sectionParts = section.split("_")

        sectionType = sectionParts[0]
        if sectionType == "Room":
            roomName = sectionParts[1]
            room = createRoom(config, roomName)
            rooms.append(room)
            print ("%s" % room)

    return rooms



