"""Socket client implementation with reconnection and timeout support."""

import socket
import logging
import time
from typing import Optional, Tuple, Union

logger = logging.getLogger(__name__)


class SocketClient:
    """Base socket client supporting TCP and UDP protocols.

    Args:
        host: Remote server hostname or IP address.
        port: Remote server port number.
        protocol: Transport protocol, "tcp" or "udp".
        timeout: Socket timeout in seconds (None for blocking).
        retries: Number of reconnection attempts on failure.
        retry_delay: Delay between reconnection attempts in seconds.
        buffer_size: Maximum receive buffer size in bytes.
    """

    def __init__(
        self,
        host: str,
        port: int,
        protocol: str = "tcp",
        timeout: Optional[float] = 30.0,
        retries: int = 3,
        retry_delay: float = 1.0,
        buffer_size: int = 4096,
    ) -> None:
        if protocol.lower() not in ("tcp", "udp"):
            raise ValueError(f"Unsupported protocol: {protocol}. Use 'tcp' or 'udp'.")

        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.buffer_size = buffer_size
        self._sock: Optional[socket.socket] = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Return whether the client is currently connected."""
        return self._connected

    def _create_socket(self) -> socket.socket:
        """Create and configure the underlying socket."""
        sock_type = socket.SOCK_STREAM if self.protocol == "tcp" else socket.SOCK_DGRAM
        sock = socket.socket(socket.AF_INET, sock_type)
        if self.timeout is not None:
            sock.settimeout(self.timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def connect(self) -> None:
        """Connect to the remote server (TCP only; UDP is connectionless).

        Raises:
            ConnectionError: If all retry attempts are exhausted.
        """
        if self.protocol == "udp":
            self._sock = self._create_socket()
            self._connected = True
            logger.info("UDP client ready (connectionless) for %s:%d", self.host, self.port)
            return

        last_error: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                self._sock = self._create_socket()
                self._sock.connect((self.host, self.port))
                self._connected = True
                logger.info(
                    "Connected to %s:%d (attempt %d/%d)",
                    self.host, self.port, attempt, self.retries,
                )
                return
            except (socket.timeout, ConnectionRefusedError, OSError) as exc:
                last_error = exc
                logger.warning(
                    "Connection attempt %d/%d failed: %s", attempt, self.retries, exc
                )
                self.close()
                if attempt < self.retries:
                    time.sleep(self.retry_delay)

        raise ConnectionError(
            f"Failed to connect to {self.host}:{self.port} after {self.retries} attempts: {last_error}"
        )

    def send(self, data: Union[str, bytes]) -> int:
        """Send data to the server.

        Args:
            data: Data to send (str is encoded as UTF-8).

        Returns:
            Number of bytes sent.

        Raises:
            ConnectionError: If the client is not connected.
        """
        if not self._connected or self._sock is None:
            raise ConnectionError("Client is not connected. Call connect() first.")

        if isinstance(data, str):
            data = data.encode("utf-8")

        if self.protocol == "udp":
            sent = self._sock.sendto(data, (self.host, self.port))
        else:
            sent = self._sock.send(data)
        logger.debug("Sent %d bytes to %s:%d", sent, self.host, self.port)
        return sent

    def receive(self, size: Optional[int] = None) -> bytes:
        """Receive data from the server.

        Args:
            size: Maximum bytes to receive (defaults to buffer_size).

        Returns:
            Received data as bytes.

        Raises:
            ConnectionError: If the client is not connected.
            socket.timeout: If the receive operation times out.
        """
        if not self._connected or self._sock is None:
            raise ConnectionError("Client is not connected. Call connect() first.")

        buf = size or self.buffer_size
        if self.protocol == "udp":
            data, _addr = self._sock.recvfrom(buf)
        else:
            data = self._sock.recv(buf)
        logger.debug("Received %d bytes from %s:%d", len(data), self.host, self.port)
        return data

    def send_and_receive(self, data: Union[str, bytes], size: Optional[int] = None) -> bytes:
        """Send data and wait for a response (convenience method).

        Args:
            data: Data to send.
            size: Maximum bytes to receive.

        Returns:
            Server response as bytes.
        """
        self.send(data)
        return self.receive(size)

    def close(self) -> None:
        """Close the socket connection."""
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError as exc:
                logger.warning("Error closing socket: %s", exc)
            finally:
                self._sock = None
                self._connected = False
                logger.info("Connection closed")

    def __enter__(self) -> "SocketClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.host!r}, port={self.port}, protocol={self.protocol!r})"


class TCPClient(SocketClient):
    """TCP socket client convenience wrapper."""

    def __init__(self, host: str, port: int, **kwargs) -> None:
        kwargs.setdefault("protocol", "tcp")
        super().__init__(host, port, **kwargs)


class UDPClient(SocketClient):
    """UDP socket client convenience wrapper."""

    def __init__(self, host: str, port: int, **kwargs) -> None:
        kwargs.setdefault("protocol", "udp")
        super().__init__(host, port, **kwargs)
