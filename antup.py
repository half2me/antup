#!/usr/bin/python

"""
Connect to AMT+ devices and upload data to a server via WebSocket
"""
from __future__ import print_function

import atexit
import sys
import json
from websocket import create_connection, socket, WebSocketConnectionClosedException
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

from profiles.PowerMessage import PowerMessage
from profiles.SpeedCadenceMessage import SpeedCadenceMessage

NETKEY = b'\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'
id = 1
bikeId = 0
servo = True

# Steppers
mh = Adafruit_MotorHAT()
stepper = mh.getStepper(200, 1)  # 200 steps/rev, motor port #1
stepper.setSpeed(30)

if len(sys.argv) >= 2:
    id = sys.argv[1]
if len(sys.argv) >= 3:
    bikeId = sys.argv[2]


def setServo(param):
    global servo
    if param != servo:
        servo = param
        if param:
            stepper.step(200, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
        else:
            stepper.step(200, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)


# Exit strategy
def graceful():
    global servo
    # Reset steppers
    if not servo:
        print("resetting wheel state")
        setServo(True)

    # Release steppers
    print("releasing motors...")
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


atexit.register(graceful)


# Callback for ANT+ events
class Listener(event.EventCallback):
    def __init__(self):
        self.previousMessageSpeedCadence = None
        self.previousMessagePower = None
        self.staleSpeedCount = [0]
        self.staleCadenceCount = [0]

    def process(self, msg, channel):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            # Speed and Cadence
            if channel.name == "speedcadence":
                decoded = SpeedCadenceMessage(self.previousMessageSpeedCadence, msg.payload, self.staleSpeedCount,
                                              self.staleCadenceCount)
                print("Speed: %f" % decoded.speed(2096))
                print("Cadence: %f" % decoded.cadence)
                print("")
                # print(".", end="")
                ws.send('{"cmd":"bike-update", "speed":' + str(decoded.speed(2096)) + ', "cadence":' + str(
                    decoded.cadence) + '}')
                self.previousMessageSpeedCadence = decoded

            # Power
            if channel.name == "power":
                if msg.payload[1] == 0x10:  # Standard Power Only!
                    decoded = PowerMessage(self.previousMessagePower, msg.payload)
                    print("Power: %f" % decoded.averagePower)
                    print("")
                    # print(".", end="")
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
channel1.setID(121, int(bikeId), 0)
channel1.searchTimeout = TIMEOUT_NEVER
channel1.period = 8086
channel1.frequency = 57
channel1.open()
channel1.registerCallback(Listener())

# Setup Power channel
channel2 = antnode.getFreeChannel()
channel2.name = 'power'
channel2.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
channel2.setID(11, int(bikeId), 0)
channel2.searchTimeout = TIMEOUT_NEVER
channel2.period = 8182
channel2.frequency = 57
channel2.open()
channel2.registerCallback(Listener())

ws = None
try:
    # Web Socket Magic
    ws = create_connection("ws://127.0.0.1:8080")
    ws.send('{"cmd":"bike-register", "id":' + str(id) + '}')

    # Run
    while True:
        recv = json.loads(ws.recv())
        print(str(recv))
        if "cmd" in recv and "value" in recv:
            if recv["cmd"] == "servo":
                setServo(bool(recv["value"]))

except socket.error as err:
    print("Disconnected!")
except WebSocketConnectionClosedException:
    print("Disconnected!")
except KeyboardInterrupt:
    print("Exiting...")

# Close off connections and ANT+
finally:
    if ws is not None:
        ws.close()
    channel1.close()
    channel1.unassign()
    channel2.close()
    channel2.unassign()
    antnode.stop()
