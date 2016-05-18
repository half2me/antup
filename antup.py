"""
Connect to AMT+ devices and upload data to a server via ZMQ
"""
from __future__ import print_function

import sys
import time

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

from config import *

from profiles.SpeedCadenceMessage import SpeedCadenceMessage

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'


# Callback for ANT+ events
class Listener(event.EventCallback):
    def process(self, msg, channel):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            if channel.name == "speedcadence":
                print("RAW: ", end="")
                for i in msg.payload:
                    print("%X" % i + " ", end="")
                print("")
                decoded = SpeedCadenceMessage(msg.payload)
                print("Cumulative Cadence Rev Count: %d" % decoded.cumulativeCadenceRevolutionCount)
                print("Cadence Event Time: %d" % decoded.cadenceEventTime)
                print("Cumulative Speed Rev Count: %d" % decoded.cumulativeSpeedRevolutionCount)
                print("Speed Event Time: %d" % decoded.speedEventTime)
                print("")
            if channel.name == "power":
                print("Power: ", end="")
                for i in msg.payload:
                    print("%X" % i + " ", end="")
                print("")


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

# Wait
time.sleep(120)

# Shutdown
channel1.close()
channel1.unassign()
channel2.close()
channel2.unassign()
antnode.stop()
