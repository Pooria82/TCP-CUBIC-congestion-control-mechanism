import unittest
import subprocess
import os
import time


class TestCombinedScenario(unittest.TestCase):
    def setUp(self):
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        self.server_process = subprocess.Popen(
            ["python", self.server_path, "--packet_loss_prob", "0.2", "--bandwidth_limit", "1024", "--variable_rtt", "true"]
        )
        time.sleep(1)  # Wait for the server to start

    def tearDown(self):
        self.server_process.terminate()
        self.server_process.wait()

    def test_combined_scenario(self):
        client_path = os.path.join(os.path.dirname(__file__), "../client.py")
        client_process = subprocess.Popen(
            ["python", client_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, _ = client_process.communicate()

        output = stdout.decode("utf-8")
        self.assertIn("Packet lost", output)
        self.assertIn("High RTT detected", output)
        self.assertIn("Bandwidth limit exceeded", output)


if __name__ == "__main__":
    unittest.main()
