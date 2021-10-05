# Scratch Server

## About

This project is part of the bigger project "Masterthesis: Learning Networks with new technologies like LoRa".
With this server, it should be possible to establish a connection between a Raspberry Pi and Scratch.

## Setup

### Variante Websockets

```shell
$ pip3 install websockets
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
