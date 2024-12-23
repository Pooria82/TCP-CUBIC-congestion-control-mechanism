import unittest
import subprocess
import os
import time


class TestStableNetwork(unittest.TestCase):
    def setUp(self):
        """
        Setup the environment for the stable network test by starting the server
        with specific network parameters.
        """
        # Set environment variables for a stable network scenario
        os.environ["PACKET_LOSS_PROB"] = "0.0"  # No packet loss
        os.environ["BANDWIDTH_LIMIT"] = "4096"  # 4 KB/s bandwidth
        os.environ["DELAYED_ACK_COUNT"] = "1"  # Immediate ACK for every packet

        # Start the server
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        self.server_process = subprocess.Popen(["python", self.server_path])
        time.sleep(1)  # Allow server to initialize

    def tearDown(self):
        """
        Terminate the server process after the test is complete.
        """
        self.server_process.terminate()
        self.server_process.wait()

    def test_stable_network(self):
        """
        Test that the client behaves correctly under stable network conditions:
        - No packet loss
        - Stable RTT
        - Proper window size adjustment
        """
        client_path = os.path.join(os.path.dirname(__file__), "../client.py")

        try:
            # Start the client
            client_process = subprocess.Popen(
                ["python", client_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # Allow up to 35 seconds for the client to complete its execution
            stdout, _ = client_process.communicate(timeout=35)
        except subprocess.TimeoutExpired:
            client_process.kill()
            self.fail("Client process timed out after 35 seconds.")

        # Decode client output
        output = stdout.decode("utf-8")
        print("\nClient Output:\n", output)

        # Assertions
        self.assertLess(output.count("Packet lost"), 5, "Too many packets lost in a stable network.")
        self.assertIn("Sample RTT", output, "RTT samples should be recorded.")
        self.assertIn("Current window size", output, "Congestion window size should be updated.")
        print("TestStableNetwork: Test passed successfully!")


if __name__ == "__main__":
    unittest.main()
