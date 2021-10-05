import asyncio
import json
import time
from datetime import datetime
import subprocess
import os
import random
import traceback
import websockets


class Logger:
    def __init__(self):
        self.debug = True

    def print(self, message):
        if self.debug:
            print(message)


class Server:

    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.python = '/usr/local/bin/python3'
        # asyncio.run(self.main())
        self.loop = asyncio.get_event_loop()
        self.log = Logger()
        self.log.print('You have to know what you are doing...')
        self.websocket_clients = set()
        self.start()

    def handle_json_input(self, input):
        try:
            if "display" in input:
                message = input['display']
                # todo: print the message to the display.
                self.log.print(f'print on display: {message}')
        except:
            self.log.print('problems with json input...')
            self.log.print(traceback.format_exc())

    async def handle_socket_connection(self, websocket, path):
        self.websocket_clients.add(websocket)
        self.log.print(f'New connection from: {websocket.remote_address} ({len(self.websocket_clients)} total)')
        try:
            # This loop will keep listening on the socket until its closed.
            async for raw_message in websocket:
                self.log.print(f'Got: [{raw_message}] from socket [{id(websocket)}]')
                try:
                    input = json.loads(raw_message)
                    self.handle_json_input(input)
                except json.decoder.JSONDecodeError:
                    self.log.print('json decoding: Error. Wrong json format.')
                except:
                    self.log.print(traceback.format_exc())
                    self.log.print('json reading was not possible')
        except websockets.exceptions.ConnectionClosedError as cce:
            pass
        finally:
            self.log.print(f'Disconnected from socket [{id(websocket)}]...')
            self.websocket_clients.remove(websocket)

    async def broadcast_random_number(self, loop):
        """Keeps sending a random # to each connected websocket client"""
        while True:
            for c in self.websocket_clients:
                num = str(random.randint(10, 20))
                self.log.print(f'Sending [{num}] to socket [{id(c)}]')
                await c.send(num)
            await asyncio.sleep(10)

    def start(self):
        try:
            socket_server = websockets.serve(self.handle_socket_connection, 'localhost', 8820)
            self.log.print(f'Started socket server: {socket_server} ...')
            self.loop.run_until_complete(socket_server)
            self.loop.run_until_complete(self.broadcast_random_number(self.loop))
            self.loop.run_forever()
        finally:
            self.loop.close()
            self.log.print(f"Successfully shutdown [{self.loop}].")


def server():
    Server()


if __name__ == '__main__':
    server()
