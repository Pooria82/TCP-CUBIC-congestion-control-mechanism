import unittest
import subprocess
import os
import time


class TestNoBandwidthLimit(unittest.TestCase):
    def setUp(self):
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        self.server_process = subprocess.Popen(
            ["python", self.server_path, "--bandwidth_limit", "100000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(1)  # Wait for the server to start

    def tearDown(self):
        # Gracefully terminate the server
        self.server_process.terminate()
        self.server_process.wait()

    def test_no_bandwidth_limit(self):
        client_path = os.path.join(os.path.dirname(__file__), "../client.py")
        client_process = subprocess.Popen(
            ["python", client_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        start_time = time.time()
        timeout = 40  # Set a timeout for the test

        try:
            while True:
                # Check if the timeout has been exceeded
                if time.time() - start_time > timeout:
                    self.fail("Test timed out.")

                # Read and print real-time server output
                server_output_line = self.server_process.stdout.readline()
                if server_output_line:
                    print(f"Server: {server_output_line.strip()}")

                # Read and print real-time client output
                client_output_line = client_process.stdout.readline()
                if client_output_line:
                    print(f"Client: {client_output_line.strip()}")

                # Break loop if the client process is finished
                if client_process.poll() is not None:
                    break

            # Ensure all output is consumed
            client_stdout, client_stderr = client_process.communicate()
            print("Client Full Output:", client_stdout)

            # Validate the output
            self.assertIn("Current window size", client_stdout)
            self.assertNotIn("Bandwidth limit exceeded", client_stdout)

        finally:
            client_process.terminate()
            client_process.wait()


if __name__ == "__main__":
    unittest.main()
