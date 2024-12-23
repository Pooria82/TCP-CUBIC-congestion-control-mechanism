import unittest
import subprocess
import os
import time


class TestNoBandwidthLimit(unittest.TestCase):
    def setUp(self):
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        self.server_process = subprocess.Popen(
            ["python", self.server_path, "--bandwidth_limit", "100000"]
        )
        time.sleep(1)  # Wait for the server to start

    def tearDown(self):
        self.server_process.terminate()
        self.server_process.wait()

    def test_no_bandwidth_limit(self):
        client_path = os.path.join(os.path.dirname(__file__), "../client.py")
        client_process = subprocess.Popen(
            ["python", client_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, _ = client_process.communicate()

        output = stdout.decode("utf-8")
        self.assertIn("Current window size", output)
        self.assertNotIn("Bandwidth limit exceeded", output)


if __name__ == "__main__":
    unittest.main()
