#!/usr/bin/python

from websocket import create_connection, socket, WebSocketConnectionClosedException
import sys
import time

if len(sys.argv) == 5:
    id = sys.argv[1]
    speed = sys.argv[2]
    cadence = sys.argv[3]
    power = sys.argv[4]
else:
    print("Usage: " + str(sys.argv[0] + " id speed cadence power"))
    exit()

ws = None
try:

    # Web Socket Magic
    ws = create_connection("ws://127.0.0.1:8080")
    ws.send('{"cmd":"bike-register", "id":' + str(id) + '}')

    while True:
        ws.send('{"cmd":"bike-update", "speed":' + str(speed) + ', "cadence":' + str(cadence) + '}')
        ws.send('{"cmd":"bike-update", "power":' + str(power) + '}')
        time.sleep(1)


except socket.error as err:
    print("Disconnected!")
except WebSocketConnectionClosedException:
    print("Disconnected!")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    if ws is not None:
        ws.close()
