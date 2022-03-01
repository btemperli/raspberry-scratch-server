# Watcher for LoRaWAN Transmissions.
# Author: beat temperli

import busio
from digitalio import DigitalInOut, Direction, Pull
import re
import board
import adafruit_ssd1306
import adafruit_rfm9x
import os
import dotenv
from threading import Thread
from WatchOutput import WatchOutput


class WatchLora(Thread):

    def __init__(self, watch_output):
        super().__init__()

        dotenv.load_dotenv()

        # Create the I2C interface.
        i2c = busio.I2C(board.SCL, board.SDA)

        # 128x32 OLED Display
        reset_pin = DigitalInOut(board.D4)
        self.display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

        # Identifiers
        self.address_set = set([])

        # Clear the display.
        self.display.fill(0)
        self.display.show()

        # Configure LoRa Radio
        cs = DigitalInOut(board.CE1)
        reset = DigitalInOut(board.D25)
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 868.1)
        self.rfm9x.tx_power = 23

        self.watchOutput = watch_output
        print('watch.py initialized.')

    def write_to_display(self, text, x, y):
        self.display.text(text, x, y, 1, font_name=os.environ.get('watcher-dir') + 'font5x8.bin')

    def handle_packet(self, packet):
        # header
        #
        # node = packet[0] // broadcast: 255 (xff)
        # node: If not 255 (0xff) then only packets address to this node will be accepted.
        #
        # destination = packet[1] // breadcast: 255 (xff)
        # destination: If 255 (0xff) then any receiving node should accept the packet.
        #
        # identifier = packet[2] // default: x00
        # identifier: Automatically set to the sequence number when send_with_ack() used.
        #
        # flags = packet[3] // default: x00
        #
        # todo: check if we should send mac-address from server as first entry and read it out here.
        # or better: the kids need to define this by themselves and sending it with the message.

        header = packet[:4]
        header_text = str(header, 'utf-16')
        print('header:', header)
        print('header:', header_text)

        packet_text = str(packet[4:], "utf-8")
        pattern = r'\[([a-z0-9:])*\]'
        matches = re.match(pattern, packet_text)
        self.display.fill(0)

        # Address is available in the packet
        if matches:
            address = matches.group()
            self.address_set.add(address)
            packet_text = re.sub(pattern, '', packet_text)
            print('packet from', address, ':', packet[4:])
            print('packet from', address, ':', packet_text)
            self.write_to_display('RX: ', 0, 0)
            self.write_to_display(packet_text, 25, 0)
            self.watchOutput.add_message(address, packet_text)

        # No address found.
        else:
            print('packet:', packet[4:])
            print('packet:', packet_text)
            self.write_to_display('RX: ', 0, 0)
            self.write_to_display(packet_text, 25, 0)
            self.watchOutput.add_message('unknown', packet_text)

        self.display.show()

    def run(self):
        print('run Watcher.py')
        self.write_to_display('ready.', 15, 20)
        self.display.show()

        while True:
            # check for packet rx
            packet = self.rfm9x.receive(with_header=True)

            if packet is not None:
                t = Thread(target=self.handle_packet, args=(packet,))
                t.start()

                # rssi = self.rfm9x.last_rssi
                # print('------')
                # print('received:', packet)
                # print('signal strength:', rssi, 'dBm')


class Manager:
    def __init__(self):
        print('init manager. starting up...')
        watch_output = WatchOutput()

        # start thread
        watch_lora = WatchLora(watch_output)
        watch_lora.setDaemon(True)
        watch_lora.start()

        # start all non-threaded functions
        watch_output.run()


if __name__ == '__main__':
    Manager()
