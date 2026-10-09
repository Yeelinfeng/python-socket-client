"""Example usage of the Python Socket Client library."""

import logging
from socket_client import TCPClient, UDPClient

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")


def tcp_example() -> None:
    """Demonstrate a TCP client connection to an echo server."""
    print("\n--- TCP Example ---")
    # Using context manager for automatic connection cleanup
    with TCPClient(host="localhost", port=8888, timeout=5.0, retries=3) as client:
        response = client.send_and_receive("Hello, TCP Server!")
        print(f"TCP Response: {response!r}")


def udp_example() -> None:
    """Demonstrate a UDP client connection."""
    print("\n--- UDP Example ---")
    client = UDPClient(host="localhost", port=9999, timeout=5.0)
    try:
        client.connect()
        client.send("Hello, UDP Server!")
        data = client.receive()
        print(f"UDP Response: {data!r}")
    finally:
        client.close()


def manual_reconnect_example() -> None:
    """Demonstrate manual reconnection on failure."""
    print("\n--- Manual Reconnect Example ---")
    client = TCPClient(host="localhost", port=8080, retries=1, retry_delay=0.5)
    try:
        client.connect()
        client.send("ping")
        print(f"Received: {client.receive()}")
    except ConnectionError as exc:
        print(f"Connection failed: {exc}")
        print("Retrying with longer timeout...")
        client.timeout = 60.0
        client.retries = 5
        client.connect()
        print("Reconnected successfully!")
    finally:
        client.close()


if __name__ == "__main__":
    # These examples require a running server on localhost
    # Start a simple test server with: python -m socket_server
    try:
        tcp_example()
    except (ConnectionError, OSError) as exc:
        print(f"TCP example skipped: {exc}")

    try:
        udp_example()
    except (ConnectionError, OSError) as exc:
        print(f"UDP example skipped: {exc}")
