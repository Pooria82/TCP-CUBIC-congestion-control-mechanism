import unittest
import subprocess
import os
import time


class TestVariableRTT(unittest.TestCase):
    def setUp(self):
        # Start the server with variable RTT enabled
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        env = os.environ.copy()
        env["VARIABLE_RTT"] = "true"  # Enable variable RTT in server
        env["PACKET_LOSS_PROB"] = "0.1"  # Set packet loss probability to 10%
        self.server_process = subprocess.Popen(
            ["python", self.server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        time.sleep(1)  # Wait for the server to start

    def tearDown(self):
        # Terminate the server and print its logs
        self.server_process.terminate()
        stdout, stderr = self.server_process.communicate()
        print("\nServer Output:\n", stdout.decode("utf-8"))
        print("\nServer Errors:\n", stderr.decode("utf-8"))
        self.server_process.wait()

    def test_variable_rtt(self):
        # Run the client
        client_path = os.path.join(os.path.dirname(__file__), "../client.py")
        try:
            client_process = subprocess.Popen(
                ["python", client_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, _ = client_process.communicate(timeout=35)
        except subprocess.TimeoutExpired:
            client_process.kill()
            self.fail("Client process timed out.")

        output = stdout.decode("utf-8")
        print("\nClient Output:\n", output)

        # Assertions to ensure correct behavior
        self.assertIn("High RTT detected", output, "Client should detect high RTT.")
        self.assertIn("Reducing window size", output, "Client should reduce window size during high RTT.")
        self.assertLess(
            output.count("High RTT detected"), 20,
            "Too many high RTT detections; mechanism may not stabilize."
        )

        print("TestVariableRTT: Test passed successfully!")


if __name__ == "__main__":
    unittest.main()
