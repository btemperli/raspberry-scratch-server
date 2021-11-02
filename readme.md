# Scratch Server

## About

This project is part of the bigger project "Masterthesis: Learning Networks with new technologies like LoRa".
With this server, it should be possible to establish a connection between a Raspberry Pi and Scratch.

## Setup

Prepare Raspberry Pi:

- enable `Interface Options` / `I2C`
- enable `Interface Options` / `SPI`

```shell
$ sudo raspi-config
```

Install required packages:

```shell
$ pip3 install websockets
$ pip3 install python-dotenv
```

Create a `.env` file and edit its content: 

```shell
$ cp example.env .env
$ nano .env
```

Connect the raspberry pi with the [LoRa Bonnet from adafruit](https://learn.adafruit.com/adafruit-radio-bonnets/rfm69-raspberry-pi-setup):

```shell
$ pip3 install adafruit-circuitpython-ssd1306
$ sudo pip3 install adafruit-circuitpython-framebuf
$ sudo pip3 install adafruit-circuitpython-rfm9x
$ wget https://github.com/adafruit/Adafruit_CircuitPython_framebuf/raw/main/examples/font5x8.bin
```

Test everything needed on the Raspberry Pi:

```shell
$ python3 test_server.py
```

## Server

### Start

```shell
$ python3 server.py
```

### Connection

With [postman](https://www.postman.com/): WebSocket Request. Connect to `localhost:8820`

### Requests

You can communicate with the server by sending json:

```json
{
    "display": "a new message"
}
```

#### Keys

| key | handling | example |
|:---:| --- | --- |
| `display` | shows a message on the [screen](https://www.adafruit.com/product/4074) of the raspberry pi | `{"display": "some output"}`
| `send` | sends a message via the [LoRa-Node](https://www.adafruit.com/product/4074) of the raspberry pi | `{"send": "a message"}`
