import socket
import threading
import random
import time


class TCPServer:
    def __init__(self, host='127.0.0.1', port=65432, packet_loss_prob=0.1, delayed_ack_count=3, bandwidth_limit=1024):
        self.host = host
        self.port = port
        self.packet_loss_prob = packet_loss_prob
        self.delayed_ack_count = delayed_ack_count
        self.bandwidth_limit = bandwidth_limit  # Maximum bytes per second
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_bandwidth_limit = self.bandwidth_limit
        self.network_busy = False  # Indicates whether the network is congested

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

                # Track bandwidth usage
                data_received += len(data)
                elapsed_time = time.time() - start_time

                # Check if bandwidth limit is exceeded
                if data_received > self.current_bandwidth_limit:
                    print("Bandwidth limit exceeded! Throttling...")
                    time.sleep(1)  # Simulate throttling by delaying ACK
                    data_received = 0
                    start_time = time.time()

                # Simulate network congestion
                if self.network_busy:
                    print("Network is busy! Delaying ACK...")
                    time.sleep(0.5)  # Delay ACK due to congestion

                print(f"Received: {data.decode()}")
                packet_counter += 1

                # Send ACK only after delayed_ack_count packets
                if packet_counter >= self.delayed_ack_count:
                    conn.sendall(b"ACK")
                    packet_counter = 0

    def simulate_network_conditions(self):
        """
        Simulate changes in network conditions, such as congestion, RTT variations, and bandwidth fluctuations.
        """
        while True:
            # Randomly simulate network congestion
            self.network_busy = random.choice([True, False])

            # Randomly adjust bandwidth limit
            self.current_bandwidth_limit = random.randint(int(self.bandwidth_limit * 0.5), self.bandwidth_limit)

            print(f"Current bandwidth limit: {self.current_bandwidth_limit} bytes/sec")
            print(f"Network busy: {self.network_busy}")

            # Wait before changing network conditions again
            time.sleep(random.uniform(5, 10))

    def stop(self):
        self.server_socket.close()


if __name__ == "__main__":
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopped.")
        server.stop()
