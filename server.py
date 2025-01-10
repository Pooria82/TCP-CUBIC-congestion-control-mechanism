import socket
import threading
import random
import time
import os


class TCPServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.packet_loss_prob = float(os.getenv("PACKET_LOSS_PROB", 0.1))
        self.delayed_ack_count = int(os.getenv("DELAYED_ACK_COUNT", 3))
        self.bandwidth_limit = int(os.getenv("BANDWIDTH_LIMIT", 1024))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_bandwidth_limit = self.bandwidth_limit
        self.network_busy = False

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server is listening on {self.host}:{self.port}")

        network_thread = threading.Thread(target=self.simulate_network_conditions, daemon=True)
        network_thread.start()

        while True:
            conn, addr = self.server_socket.accept()
            print(f"Connected by {addr}")
            thread = threading.Thread(target=self.handle_client, args=(conn,))
            thread.start()

    def print_parameters(self):
        print(f"\n=== Server Parameters ===")
        print(f"Packet Loss Probability: {self.packet_loss_prob}")
        print(f"Bandwidth Limit: {self.current_bandwidth_limit} bytes/sec")
        print(f"Delayed ACK Count: {self.delayed_ack_count}")
        print(f"Network Busy: {self.network_busy}")

    def handle_client(self, conn):
        try:
            with conn:
                packet_counter = 0
                data_received = 0
                start_time = time.time()

                while True:
                    data = conn.recv(1024)
                    if not data:
                        break

                    if random.random() < self.packet_loss_prob:
                        print("Packet lost!")
                        continue

                    data_received += len(data)
                    elapsed_time = time.time() - start_time

                    if data_received > self.current_bandwidth_limit:
                        print("Bandwidth limit exceeded! Throttling...")
                        time.sleep(1)
                        data_received = 0
                        start_time = time.time()

                    if self.network_busy:
                        print("Network is busy! Delaying ACK...")
                        time.sleep(0.5)

                    print(f"Received: {data.decode()}")
                    packet_counter += 1

                    if packet_counter >= self.delayed_ack_count:
                        conn.sendall(b"ACK")
                        packet_counter = 0

                    self.print_parameters()

        finally:
            print("Closing connection.")
            conn.close()

    def simulate_network_conditions(self):
        while True:
            self.network_busy = random.choice([True, False])
            self.current_bandwidth_limit = random.randint(
                int(self.bandwidth_limit * 0.8), self.bandwidth_limit
            )
            self.print_parameters()
            time.sleep(10)

    def stop(self):
        self.server_socket.close()


if __name__ == "__main__":
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
        server.stop()
