#!/usr/bin/python

"""
Connect to AMT+ devices and upload data to a server via WebSocket
"""
from __future__ import print_function

import sys
import time

from websocket import create_connection

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

from profiles.PowerMessage import PowerMessage
from profiles.SpeedCadenceMessage import SpeedCadenceMessage

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

# Callback for ANT+ events
class Listener(event.EventCallback):

    def __init__(self):
        self.previousMessageSpeedCadence = None
        self.previousMessagePower = None

    def process(self, msg, channel):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            # Speed and Cadence
            if channel.name == "speedcadence":
                decoded = SpeedCadenceMessage(self.previousMessageSpeedCadence, msg.payload)

                print("Speed: %f" % decoded.speed(2096))
                print("Cadence: %f" % decoded.cadence)
                print("")
                ws.send('{"cmd":"bike-update", "speed":' + str(decoded.speed(2096)) + ', "cadence":' + str(decoded.cadence) + '}')
                self.previousMessageSpeedCadence = decoded

            # Power
            if channel.name == "power":
                if msg.payload[1] == 0x10: # Standard Power Only!
                    decoded = PowerMessage(self.previousMessagePower, msg.payload)
                    print("Power: %f" % decoded.averagePower)
                    print("")
                    ws.send('{"cmd":"bike-update", "power":' + str(decoded.averagePower) + '}')
                    self.previousMessagePower = None


# Initialize
stick = driver.USB2Driver(idProduct=0x1009)
antnode = node.Node(stick)
antnode.start()

network = node.Network(NETKEY, 'N:ANT+')
antnode.setNetworkKey(0, network)

# Setup Speed & Cadence sensor channel
channel1 = antnode.getFreeChannel()
channel1.name = "speedcadence"
channel1.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
channel1.setID(121, 0, 0)
channel1.searchTimeout = TIMEOUT_NEVER
channel1.period = 8086
channel1.frequency = 57
channel1.open()
channel1.registerCallback(Listener())

# Setup Power channel
channel2 = antnode.getFreeChannel()
channel2.name = 'power'
channel2.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
channel2.setID(11, 0, 0)
channel2.searchTimeout = TIMEOUT_NEVER
channel2.period = 8182
channel2.frequency = 57
channel2.open()
channel2.registerCallback(Listener())

# Web Socket Magic
ws = create_connection("ws://127.0.0.1:8080")
ws.send(u'{"cmd":"bike-register", "id":1}'.encode('utf8'))

# Wait
time.sleep(60*60)

# Shutdown
channel1.close()
channel1.unassign()
channel2.close()
channel2.unassign()
antnode.stop()
ws.close()