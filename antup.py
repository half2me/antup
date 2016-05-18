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
from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

from config import *


class AntRaceProtocol(WebSocketClientProtocol):

   def register(self):
      self.sendMessage("Hello, world!")

   def onOpen(self):
      self.sendMessage("register")

   def onMessage(self, msg, binary):
      print ("Got message: " + msg)

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'


# Speed EL
class Listener(event.EventCallback):
    def process(self, msg, channel):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            print("Speed: ", end="")
            for i in msg.payload:
                print("%X" % i + " ", end="")
            print("")
            data = {'bike_id': 1, 'timestamp': time.time(), channel.name: 50}
            socket.send_json(data)
            print("Sent!")
            # Add lock to method since sockets are not thread-safe


# Initialize
stick = driver.USB2Driver(idProduct=0x1008)
antnode = node.Node(stick)
antnode.start()

network = node.Network(NETKEY, 'N:ANT+')
antnode.setNetworkKey(0, network)

# Setup Speed channel
channel1 = antnode.getFreeChannel()
channel1.name = 'speed'
channel1.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
channel1.setID(123, 0, 0)
channel1.searchTimeout = TIMEOUT_NEVER
channel1.period = 8118
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
factory = WebSocketClientFactory("ws://localhost:8080")
factory.protocol = AntRaceProtocol
connectWS(factory)
reactor.run()

# Wait
print("Sleeping")
time.sleep(120)

# Shutdown
channel1.close()
channel1.unassign()
antnode.stop()
