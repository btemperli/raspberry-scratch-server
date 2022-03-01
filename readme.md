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
$ sudo pip3 install -r requirements.txt
```

Create a `.env` file and edit its content: 

```shell
$ cp example.env .env
$ nano .env
```

Connect the raspberry pi with the [LoRa Bonnet from adafruit](https://learn.adafruit.com/adafruit-radio-bonnets/rfm69-raspberry-pi-setup):

```shell
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


## Updates

### Requirements

You can add used packages to the `requirements.txt` in the root-folder. Use the following command to show all installed packages:

```shell
$ sudo pip freeze
```

You can update a specific package with the following command:

    $ sudo pip install --upgrade adafruit-circuitpython-rfm9x


## Bugs

### Font Module

```python
⚠️ NotImplementedError: font module not available (ImportError: libSDL2_ttf-2.0.so.0: cannot open shared object file: No such file or directory)
```

#### Solution

    $ sudo apt install libsdl2-ttf-2.0-0

---

# Watcher

A second module in this project is the watcher. With the watcher, you can watch the sending streams from the different scratch-server-applications.

## Run watcher

    $ python3 Watcher.py

*You cannot run the Watcher from an external console, because it needs a display to show the incoming messages.*

## Add the watcher to autostart

    $ sudo nano /etc/xdg/lxsession/LXDE-pi/autostart

Now add the following line before the screensaver line:

    @/usr/bin/python3 /home/pi/raspberry-scratch-server/Watcher.py > /home/pi/watcher.log 2>&1