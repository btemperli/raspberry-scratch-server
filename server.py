import asyncio
import json
import random
import traceback
import websockets
import dotenv
import os

# display
# from digitalio import DigitalInOut
# import adafruit_ssd1306
# import busio
# import board

# load .env file
dotenv.load_dotenv()


class Logger:
    def __init__(self):
        self.debug = True

    def print(self, message):
        if self.debug:
            print(message)


class Display:
    def __init__(self):
        self.environment = os.environ.get('environment')
        self.available_display = self.environment == 'raspberry'
        if self.available_display:

            from digitalio import DigitalInOut
            import adafruit_ssd1306
            import busio
            import board

            # Create the I2C interface.
            i2c = busio.I2C(board.SCL, board.SDA)

            # 128x32 OLED Display
            reset_pin = DigitalInOut(board.D4)
            self.display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
            # Clear the display.
            self.display.fill(0)
            self.display.show()
            self.width = self.display.width
            self.height = self.display.height
        else:
            self.display = None

    def print(self, message):
        if self.available_display:
            self.display.text(message, 0, 0, 1)
            self.display.show()
        else:
            print('show on display:')
            print(message)


class Server:

    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.python = '/usr/local/bin/python3'
        # asyncio.run(self.main())
        self.loop = asyncio.get_event_loop()
        self.log = Logger()
        self.display = Display()
        self.log.print('You have to know what you are doing...')
        self.websocket_clients = set()
        self.start()

    def handle_json_message(self, json_message):
        try:
            if "display" in json_message:
                display_message = json_message['display']
                # self.log.print(f'print on display: {display_message}')
                self.display.print(display_message)
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
                    decoded_message = json.loads(raw_message)
                    self.handle_json_message(decoded_message)
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
            socket_server = websockets.serve(
                self.handle_socket_connection,
                os.environ.get('server-ip'),
                os.environ.get('server-port'))
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
