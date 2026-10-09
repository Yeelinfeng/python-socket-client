"""Unit tests for the socket_client library."""

import socket
import threading
import pytest
from socket_client import SocketClient, TCPClient, UDPClient


@pytest.fixture
def tcp_server():
    """Start a simple TCP echo server for testing."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    host, port = server.getsockname()

    def handle(conn):
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                conn.sendall(data)
        except OSError:
            pass
        finally:
            conn.close()

    thread = threading.Thread(target=lambda: _accept_loop(server, handle), daemon=True)
    thread.start()
    yield host, port
    server.close()


def _accept_loop(server, handler):
    while True:
        try:
            conn, _ = server.accept()
        except OSError:
            break
        t = threading.Thread(target=handler, args=(conn,), daemon=True)
        t.start()


@pytest.fixture
def udp_server():
    """Start a simple UDP echo server for testing."""
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    host, port = server.getsockname()

    def handle():
        try:
            while True:
                data, addr = server.recvfrom(4096)
                if not data:
                    break
                server.sendto(data, addr)
        except OSError:
            pass
        finally:
            server.close()

    thread = threading.Thread(target=handle, daemon=True)
    thread.start()
    yield host, port


class TestSocketClient:
    def test_invalid_protocol_raises(self):
        with pytest.raises(ValueError, match="Unsupported protocol"):
            SocketClient("localhost", 80, protocol="icmp")

    def test_repr(self):
        client = TCPClient("example.com", 443)
        assert "TCPClient" in repr(client)
        assert "example.com" in repr(client)
        assert "443" in repr(client)

    def test_not_connected_raises_on_send(self):
        client = TCPClient("localhost", 80)
        with pytest.raises(ConnectionError, match="not connected"):
            client.send("hello")

    def test_not_connected_raises_on_receive(self):
        client = TCPClient("localhost", 80)
        with pytest.raises(ConnectionError, match="not connected"):
            client.receive()


class TestTCPClient:
    def test_connect_and_echo(self, tcp_server):
        host, port = tcp_server
        with TCPClient(host, port, timeout=5.0) as client:
            assert client.is_connected
            client.send("hello")
            data = client.receive()
            assert data == b"hello"

    def test_send_and_receive(self, tcp_server):
        host, port = tcp_server
        with TCPClient(host, port, timeout=5.0) as client:
            resp = client.send_and_receive("ping")
            assert resp == b"ping"

    def test_close_disconnects(self, tcp_server):
        host, port = tcp_server
        client = TCPClient(host, port, timeout=5.0)
        client.connect()
        assert client.is_connected
        client.close()
        assert not client.is_connected


class TestUDPClient:
    def test_udp_send_receive(self, udp_server):
        host, port = udp_server
        client = UDPClient(host, port, timeout=5.0)
        try:
            client.connect()
            assert client.is_connected
            client.send("hello udp")
            data = client.receive()
            assert data == b"hello udp"
        finally:
            client.close()
