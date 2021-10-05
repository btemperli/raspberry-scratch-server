import board
import digitalio
import busio

print('Running some tests to check packages, libraries & adafruit bonnet')

# blinka-tests
# @see https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
print('-------------------------')
print('blinka-test is running...')

# Try to great a Digital input
pin = digitalio.DigitalInOut(board.D4)
print('Digital IO ok!')

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print('I2C ok!')

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print('SPI ok!')

print('...blinka-test successful')
print('-------------------------')

