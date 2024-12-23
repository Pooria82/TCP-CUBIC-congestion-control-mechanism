import socket
import threading
import random
import time


class TCPServer:
    def __init__(self, host='127.0.0.1', port=65432, packet_loss_prob=0.02, delayed_ack_count=3, bandwidth_limit=2048):
        self.host = host
        self.port = port
        self.packet_loss_prob = packet_loss_prob  # Packet loss probability reduced
        self.delayed_ack_count = delayed_ack_count
        self.bandwidth_limit = bandwidth_limit  # Maximum bytes per second
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_bandwidth_limit = self.bandwidth_limit
        self.network_busy = False  # No congestion for stable network

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server is listening on {self.host}:{self.port}")

        # Start a thread to simulate network conditions
        network_simulation_thread = threading.Thread(target=self.simulate_network_conditions)
        network_simulation_thread.daemon = True
        network_simulation_thread.start()

        while True:
            conn, addr = self.server_socket.accept()
            print(f"Connected by {addr}")
            thread = threading.Thread(target=self.handle_client, args=(conn,))
            thread.start()

    def handle_client(self, conn):
        with conn:
            packet_counter = 0
            data_received = 0
            start_time = time.time()

            while True:
                data = conn.recv(1024)
                if not data:
                    break

                # Simulate packet loss
                if random.random() < self.packet_loss_prob:
                    print("Packet lost!")
                    continue

                print(f"Received: {data.decode()}")
                packet_counter += 1

                # Send ACK only after delayed_ack_count packets
                if packet_counter >= self.delayed_ack_count:
                    conn.sendall(b"ACK")
                    packet_counter = 0

    def simulate_network_conditions(self):
        """
        Simulate stable network conditions for the test.
        """
        while True:
            self.network_busy = False  # Stable network
            self.current_bandwidth_limit = self.bandwidth_limit  # Fixed high bandwidth
            print(f"Stable network: Bandwidth = {self.current_bandwidth_limit}, Network busy = {self.network_busy}")
            time.sleep(5)

    def stop(self):
        self.server_socket.close()


if __name__ == "__main__":
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopped.")
        server.stop()
