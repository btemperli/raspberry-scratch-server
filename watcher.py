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
    packet = rfm9x.receive()
    if packet is None:
        display.text('waiting', 15, 20, 1)
        display.show()
    else:
        print('------')
        print(packet)
        prev_packet = packet
        packet_text = str(prev_packet, "utf-8")
        print(packet_text)
        display.text('RX: ', 0, 0, 1)
        display.text(packet_text, 25, 0, 1)
        display.show()
        time.sleep(1)