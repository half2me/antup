"""
Connect to AMT+ devices and upload data to a server via ZMQ
"""

import sys
import time
#import zmq

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

from config import *

# ZMQ
#zcontext = zmq.Context()
#socket = zcontext.socket(zmq.REQ)
#socket.connect ("tcp://middle-layer-ip:9999")

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'


# A run-the-mill event listener
class Listener(event.EventCallback):
    def process(self, msg):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            #print 'Speed:', ord(msg.payload[-1])
            print 'yolo'
            #socket.send(ord(msg.payload[-1])) # Change this to JSON data
            # Add lock to method since sockets are not thread-safe


# Initialize
stick = driver.USB2Driver(idProduct=0x1009)
antnode = node.Node(stick)
antnode.start()

# Setup channel
network = node.Network(NETKEY, 'N:ANT+')
antnode.setNetworkKey(0, network)
channel = antnode.getFreeChannel()
channel.name = 'C:Speed'
channel.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
channel.setID(123, 0, 0)
channel.searchTimeout = TIMEOUT_NEVER
channel.period = 8118
channel.frequency = 57
channel.open()

# Setup callback
# Note: We could also register an event listener for non-channel events by
# calling registerEventListener() on antnode rather than channel.
channel.registerCallback(Listener())

# Wait
print "Listening for HR monitor events (120 seconds)..."
time.sleep(120)

# Shutdown
channel.close()
channel.unassign()
antnode.stop()
