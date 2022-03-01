import asyncio
import json
import random
import traceback
import websockets
import dotenv
import os
import signal
import sys
from getmac import get_mac_address


# handle exit command comming from bash-script.
# https://stackoverflow.com/a/24574672/2241151
def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    print('sigterm_handler', flush=True)
    print(_signo, flush=True)
    sys.exit(0)


if len(sys.argv) > 1 and sys.argv[1] == "handle_exit_signal":
    signal.signal(signal.SIGTERM, sigterm_handler)

# load .env file
dotenv.load_dotenv()


class Logger:
    def __init__(self):
        self.debug = True

    def print(self, message):
        if self.debug:
            print(message, flush=True)


class LoRa:
    def __init__(self, logger):
        self.logger = logger
        self.environment = os.environ.get('environment')
        self.available_lora = self.environment == 'raspberry'
        self.prev_packet = None

        if self.available_lora:
            from digitalio import DigitalInOut
            import busio
            import board
            import adafruit_ssd1306
            import adafruit_rfm9x

            # Configure LoRa Radio
            CS = DigitalInOut(board.CE1)
            RESET = DigitalInOut(board.D25)
            spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            self.rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 868.1)
            self.rfm9x.tx_power = 23
            self.eth_mac = get_mac_address(interface="eth0")

            # possible configuration
            # @see https://circuitpython.readthedocs.io/projects/rfm9x/en/latest/
            # Apply new modem config settings to the radio to improve its effective range
            # rfm9x.signal_bandwidth = 62500
            # rfm9x.coding_rate = 6
            # rfm9x.spreading_factor = 8
            # rfm9x.enable_crc = True

    def read(self):
        if not self.available_lora:
            self.logger.print('Nothing to receive on a computer...')
            return None

        packet = self.rfm9x.receive()
        if packet is None:
            # do nothing, no message read.
            return None

        self.logger.print('------')
        self.logger.print(packet)
        self.prev_packet = packet
        packet_text = str(self.prev_packet, "utf-8")
        self.logger.print(packet_text)
        return packet_text

    def send(self, message):
        message_data = bytes("[" + self.eth_mac + "]"+message, encoding="utf-8")

        if not self.available_lora:
            self.logger.print('send text: ' + message)
            self.logger.print('send bytes: ' + str(message_data))
            return

        self.rfm9x.send(message_data)


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
            self.display.fill(0)

            # prevent missing font files
            self.display.text(str(message), 0, 0, 1)
            self.display.show()
        else:
            print('show on display:')
            print(str(message))


class Server:

    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.python = '/usr/local/bin/python3'
        self.loop = asyncio.get_event_loop()
        self.log = Logger()
        self.display = Display()
        self.lora = LoRa(self.log)
        self.display.print('server up and running')
        self.websocket_clients = set()
        self.start()

    def handle_json_message(self, json_message):
        try:
            if "display" in json_message:
                display_message = json_message['display']
                self.display.print(display_message)
            if "send" in json_message:
                send_message = json_message['send']
                self.lora.send(send_message)

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
