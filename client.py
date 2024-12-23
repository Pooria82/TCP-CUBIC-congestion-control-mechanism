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
        self.high_rtt_threshold = 0.3  # RTT threshold for detection
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
        Update the Exponential Moving Average (EMA) of RTT and check for high RTT.
        """
        self.ema_rtt = (1 - self.alpha) * self.ema_rtt + self.alpha * sample_rtt
        if self.ema_rtt > self.high_rtt_threshold:
            print(f"High RTT detected: EMA RTT = {self.ema_rtt:.3f} seconds")

    def send_data(self):
        K = self.calculate_K()
        in_slow_start = True
        in_fast_recovery = False  # Track Fast Recovery state
        start_time = time.time()

        while time.time() - start_time < 30:  # Stop after 30 seconds
            try:
                t = time.time() - self.t_start
                if in_slow_start:
                    self.W = min(self.W * 2, self.ssthresh)  # Exponential increase in Slow Start
                elif in_fast_recovery:
                    self.W += 1  # Linear increase during Fast Recovery
                    print("Fast Recovery: Increasing window linearly.")
                else:
                    self.W = self.cubic_window(t, K, self.C, self.W_max)

                successful_packets = 0
                for _ in range(int(self.W)):
                    try:
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
                            self.update_ema_rtt(sample_rtt)
                            print(f"Sample RTT: {sample_rtt:.3f} seconds, EMA RTT: {self.ema_rtt:.3f} seconds")
                    except socket.timeout:
                        print("Packet lost: Timeout waiting for ACK")
                        in_fast_recovery = True  # Enter Fast Recovery mode
                        break

                if successful_packets < self.W:
                    self.ssthresh = max(1, self.W / 2)
                    self.W = max(1, self.ssthresh)
                    in_slow_start = False
                    in_fast_recovery = True  # Transition to Fast Recovery
                    self.t_start = time.time()
                    print("Fast Recovery: Reducing window size.")
                else:
                    in_fast_recovery = False  # Exit Fast Recovery
                    if in_slow_start and self.W >= self.ssthresh:
                        in_slow_start = False
                    self.W_max = max(self.W_max, self.W)

                if self.ema_rtt > self.high_rtt_threshold:
                    print("High RTT detected, reducing window size...")
                    self.W = max(1, self.W / 2)
                    self.t_start = time.time()

                print(f"Current window size: {self.W:.2f}")
                time.sleep(self.ema_rtt)
            except KeyboardInterrupt:
                print("Client stopped.")
                break

        print("Client finished sending data.")

    def disconnect(self):
        self.socket.close()


if __name__ == "__main__":
    client = TCPClient()
    try:
        client.connect()
        client.send_data()
    except KeyboardInterrupt:
        client.disconnect()
