import unittest
import subprocess
import os
import time


class TestStableNetwork(unittest.TestCase):
    def setUp(self):
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        self.server_process = subprocess.Popen(["python", self.server_path])
        time.sleep(1)  # Wait for the server to start

    def tearDown(self):
        self.server_process.terminate()
        self.server_process.wait()

    def test_stable_network(self):
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

        # Allow up to 15 packet losses for this test
        self.assertLess(output.count("Packet lost"), 16, "Too many packets lost in a stable network")
        self.assertIn("Sample RTT", output, "RTT samples should be recorded.")
        self.assertIn("Current window size", output, "Congestion window size should be updated.")
        print("TestStableNetwork: Test passed successfully!")


if __name__ == "__main__":
    unittest.main()
