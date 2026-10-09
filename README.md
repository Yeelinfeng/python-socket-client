# Python Socket Client

A reusable TCP/UDP socket client library with reconnection and timeout support.

## Features

- **TCP and UDP support** via a unified `SocketClient` API
- **Automatic reconnection** with configurable retry count and delay
- **Timeout handling** for connect, send, and receive operations
- **Context manager** support for clean resource management
- **Logging** with Python's `logging` module
- **Type hints** throughout the codebase

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from socket_client import TCPClient

# Using context manager (auto-connect/close)
with TCPClient("localhost", 8888, timeout=5.0) as client:
    response = client.send_and_receive("Hello, Server!")
    print(response)
```

## Usage

### TCP Client

```python
from socket_client import TCPClient

client = TCPClient("example.com", 8080, timeout=10.0, retries=3, retry_delay=1.0)
try:
    client.connect()
    client.send("GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
    data = client.receive()
    print(data.decode())
finally:
    client.close()
```

### UDP Client

```python
from socket_client import UDPClient

client = UDPClient("127.0.0.1", 9999, timeout=5.0)
client.connect()
client.send("Hello UDP!")
response = client.receive()
client.close()
```

### Manual Reconnection

```python
from socket_client import TCPClient

client = TCPClient("localhost", 8080, retries=1)
try:
    client.connect()
except ConnectionError:
    # Adjust parameters and retry
    client.timeout = 60.0
    client.retries = 5
    client.connect()
```

## API Reference

### `SocketClient(host, port, protocol, timeout, retries, retry_delay, buffer_size)`

Base socket client class.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | `str` | required | Server hostname or IP |
| `port` | `int` | required | Server port |
| `protocol` | `str` | `"tcp"` | `"tcp"` or `"udp"` |
| `timeout` | `float\|None` | `30.0` | Socket timeout in seconds |
| `retries` | `int` | `3` | Connection retry attempts |
| `retry_delay` | `float` | `1.0` | Delay between retries |
| `buffer_size` | `int` | `4096` | Receive buffer size |

### `TCPClient(host, port, **kwargs)`

TCP client wrapper. Same parameters as `SocketClient` with `protocol="tcp"`.

### `UDPClient(host, port, **kwargs)`

UDP client wrapper. Same parameters as `SocketClient` with `protocol="udp"`.

## Testing

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## License

MIT
