# Dieses Script versucht die SOC an die Gegebenheit(Volt) der Akkus anzupassen
import time
import paho.mqtt.client as mqtt
import datetime
import logging
import json

verbunden = 0
cerboserial = "123456789"    # Ist auch gleich VRM Portal ID
broker_address = "192.168.1.xxx"

#  Monate sind 01 für Jan usw.

minsoc1 = ["01", "12"]
minsoc2 = ["02", "03", "10", "11"]
minsoc3 = ["04", "05", "06", "07", "08", "09"]

#  MinSoc limit

minsocp1 = "60"
minsocp2 = "35"
minsocp3 = "15"

#  Ab hier muss nichts mehr eingestellt werden!
m = 1
setminSoc = '{"value": 35}'

logging.basicConfig(filename='Error.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

def on_disconnect(client, userdata, rc):
    global verbunden
    print("Client Got Disconnected")
    if rc != 0:
        print('Unexpected MQTT disconnection. Will auto-reconnect')

    else:
        print('rc value:' + str(rc))

    try:
        print("Trying to Reconnect")
        client.connect(broker_address)
        verbunden = 1
    except Exception as e:
        logging.exception("Fehler beim reconnecten mit Broker")
        print("Error in Retrying to Connect with Broker")
        verbunden = 0
        print(e)

def on_connect(client, userdata, flags, rc):
        global verbunden
        if rc == 0:
            print("Connected to MQTT Broker!")
            verbunden = 1
            client.subscribe("N/" + cerboserial + "/settings/0/Settings/CGwacs/BatteryLife/MinimumSocLimit")
        else:
            print("Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    try:

        global minsoclimit
        if msg.topic == "N/" + cerboserial + "/settings/0/Settings/CGwacs/BatteryLife/MinimumSocLimit":   # minSocLimit

            minsoclimit = json.loads(msg.payload)
            minsoclimit = round(float(minsoclimit['value']), 2)

    except Exception as e:
        print(e)
        print("Im MSBM Programm ist etwas beim auslesen der Nachrichten schief gegangen")

# Konfiguration MQTT
client = mqtt.Client("minsocbymonth")  # create new instance
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address)  # connect to broker

logging.debug("Programm MinSoc by Month wurde gestartet")

client.loop_start()
time.sleep(1)
print("Aktueller MinSoc: " + str(minsoclimit))
aktuellermonat = datetime.datetime.now().strftime("%m")
print("Der aktuelle Monat: " + str(aktuellermonat))

while (1):
    m = 1+m
    time.sleep(1)
    if aktuellermonat in minsoc1:
        print("In diesen Monat sollte: " + str(minsocp1) + "% gesetzt sein")
        client.publish("W/" + cerboserial + "/settings/0/Settings/CGwacs/BatteryLife/MinimumSocLimit",
                                             '{"value": ' + minsocp1 + '}')
    elif aktuellermonat in minsoc2:
        print("In diesen Monat sollte: " + str(minsocp2) + "% gesetzt sein")
        client.publish("W/" + cerboserial + "/settings/0/Settings/CGwacs/BatteryLife/MinimumSocLimit",
                                            '{"value": ' + minsocp2 + '}')
    elif aktuellermonat in minsoc3:
        print("In diesen Monat sollte: " + str(minsocp3) + "% gesetzt sein")
        client.publish("W/" + cerboserial + "/settings/0/Settings/CGwacs/BatteryLife/MinimumSocLimit",
                                            '{"value": ' + minsocp3 + '}')
    else:
        print("?, der aktuelle Monat wurde nicht in einer der 3 Listen gefunden, schau nochmal oben, ob du alle Monate vergeben hast")

    now = datetime.datetime.now
    to = (now() + datetime.timedelta(days = 1)).replace(hour=13, minute=0, second=0)
    sekundenbisnext = ((to-now()).seconds)
    stundenbisnext = str(datetime.timedelta(seconds = sekundenbisnext))
    print("Schlafe nun: " + stundenbisnext + " Stunden bis um 13Uhr.")
    time.sleep((to-now()).seconds)