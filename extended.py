import sys
import time
import struct

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

from config import *

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

#channel = None

# A run-the-mill event listener
class HRMListener(event.EventCallback):
    def process(self, msg):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            print 'Heart Rate:', ord(msg.payload[8])
            #msg = message.ChannelRequestMessage(message_id=MESSAGE_CHANNEL_ID)

            #channel.node.driver.write(msg.encode())
            #try:
            #    print len(msg.payload)
            #    print type(msg.payload)
            #    test = struct.unpack('BBBBBBBBB',msg.payload)
           # except Exception, e:
            #    print e
            #print test
            #print 'hi'
            #for i in range(0,8):
            #    print ord(msg.payload[i])

# Initialize
stick = driver.USB2Driver(None)
antnode = node.Node(stick)
antnode.start()

# Setup channel
key = node.NetworkKey('N:ANT+', NETKEY)
antnode.setNetworkKey(0, key)
channel = antnode.getFreeChannel()
channel.name = 'C:HRM'
channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
channel.setID(120, 0, 0)
channel.setSearchTimeout(TIMEOUT_NEVER)
channel.setPeriod(8070)
channel.setFrequency(57)
channel.open()


# Setup callback
# Note: We could also register an event listener for non-channel events by
# calling registerEventListener() on antnode rather than channel.
channel.registerCallback(HRMListener())

# Wait
print "Listening for HR monitor events (120 seconds)..."
time.sleep(240)

# Shutdown
channel.close()
channel.unassign()
antnode.stop()