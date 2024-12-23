import unittest
import subprocess
import os
import time


class TestHighPacketLoss(unittest.TestCase):
    def setUp(self):
        # Start the server with high packet loss probability
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        self.server_process = subprocess.Popen(
            ["python", self.server_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={"PACKET_LOSS_PROB": "0.3"}
        )
        time.sleep(1)  # Wait for the server to start

    def tearDown(self):
        self.server_process.terminate()
        self.server_process.wait()

    def test_high_packet_loss(self):
        # Run the client
        client_path = os.path.join(os.path.dirname(__file__), "../client.py")
        try:
            client_process = subprocess.Popen(
                ["python", client_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, _ = client_process.communicate(timeout=35)
        except subprocess.TimeoutExpired:
            client_process.kill()
            self.fail("Client process timed out.")

        output = stdout.decode("utf-8")
        print("\nClient Output:\n", output)

        # Ensure that "Packet lost" appears in the output
        self.assertIn("Packet lost", output, "Client should detect packet loss.")
        self.assertIn("Fast Recovery", output, "Client should enter fast recovery mode.")
        self.assertLess(output.count("Packet lost"), 50, "Too many packets lost in high packet loss scenario.")
        self.assertIn("Current window size", output, "Congestion window size should be updated.")
        print("TestHighPacketLoss: Test passed successfully!")


if __name__ == "__main__":
    unittest.main()
