import socket
import time


class TCPClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.C = 0.4  # CUBIC constant
        self.W_max = 10  # Maximum congestion window
        self.W = 1  # Initial congestion window
        self.ssthresh = 5  # Slow Start threshold
        self.rtt = 0.1  # Default RTT
        self.ema_rtt = 0.1  # Exponential Moving Average for RTT
        self.alpha = 0.125  # EMA coefficient
        self.t_start = time.time()

    def connect(self):
        self.socket.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")

    def cubic_window(self, t, K, C, W_max):
        return C * (t - K) ** 3 + W_max

    def calculate_K(self):
        return (self.W_max / self.C) ** (1 / 3)

    def update_ema_rtt(self, sample_rtt):
        """
        Update the Exponential Moving Average (EMA) of RTT.
        """
        self.ema_rtt = (1 - self.alpha) * self.ema_rtt + self.alpha * sample_rtt

    def send_data(self):
        K = self.calculate_K()
        in_slow_start = True

        while True:
            try:
                # Calculate the current congestion window size
                t = time.time() - self.t_start
                if in_slow_start:
                    self.W = self.W * 2  # Exponential increase in Slow Start
                else:
                    self.W = self.cubic_window(t, K, self.C, self.W_max)

                successful_packets = 0
                for _ in range(int(self.W)):
                    try:
                        # Measure RTT
                        send_time = time.time()

                        # Send data packet
                        self.socket.sendall(b"Data packet")

                        # Wait for ACK
                        self.socket.settimeout(1)
                        data = self.socket.recv(1024)
                        receive_time = time.time()

                        if data.decode() == "ACK":
                            successful_packets += 1
                            sample_rtt = receive_time - send_time
                            self.update_ema_rtt(sample_rtt)  # Update EMA of RTT
                            print(f"Sample RTT: {sample_rtt:.3f} seconds, EMA RTT: {self.ema_rtt:.3f} seconds")
                    except socket.timeout:
                        print("Packet lost: Timeout waiting for ACK")
                        break

                # Adjust congestion window size
                if successful_packets < self.W:
                    # Packet Loss Detected
                    self.ssthresh = self.W / 2
                    self.W = max(1, self.ssthresh)  # Fast Recovery
                    in_slow_start = True
                    self.t_start = time.time()
                else:
                    if in_slow_start and self.W >= self.ssthresh:
                        in_slow_start = False  # Exit Slow Start
                    self.W_max = max(self.W_max, self.W)

                # Adjust sending rate based on RTT
                if self.ema_rtt > 0.2:  # If RTT is too high, assume congestion
                    print("High RTT detected, reducing window size...")
                    self.W = max(1, self.W / 2)
                    self.t_start = time.time()

                print(f"Current window size: {self.W:.2f}")
                time.sleep(self.ema_rtt)  # Adjust sending rate based on EMA RTT

            except KeyboardInterrupt:
                print("Client stopped.")
                break

    def disconnect(self):
        self.socket.close()


if __name__ == "__main__":
    client = TCPClient()
    try:
        client.connect()
        client.send_data()
    except KeyboardInterrupt:
        client.disconnect()
