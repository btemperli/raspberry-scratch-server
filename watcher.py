# Watcher for LoRaWAN Transmissions.
# Author: beat temperli

import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_ssd1306
import adafruit_rfm9x

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 868.1)
rfm9x.tx_power = 23
prev_packet = None

while True:
    packet = None

    # draw a box to clear the image
    display.fill(0)

    # check for packet rx
    packet = rfm9x.receive(with_header=True)
    if packet is None:
        display.text('waiting', 15, 20, 1)
        display.show()
    else:
        rssi = rfm9x.last_rssi
        print('------')
        print('received:', packet)
        print('signal strength:', rssi, 'dBm')
        prev_packet = packet
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

        header = prev_packet[:4]
        header_text = str(header, 'utf-16')
        print('header:', header)
        print('header:', header_text)
        packet_text = str(prev_packet[4:], "utf-8")

        print('packet:', prev_packet[4:])
        print('packet:', packet_text)
        display.text('RX: ', 0, 0, 1)
        display.text(packet_text, 25, 0, 1)
        display.show()
        time.sleep(1)