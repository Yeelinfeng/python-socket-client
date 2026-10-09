"""Python Socket Client - A reusable TCP/UDP socket client library."""

from .client import SocketClient, TCPClient, UDPClient

__version__ = "1.0.0"
__all__ = ["SocketClient", "TCPClient", "UDPClient"]
