import unittest
import subprocess
import os
import time


class TestVariableRTT(unittest.TestCase):
    def setUp(self):
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        env = os.environ.copy()
        env["PACKET_LOSS_PROB"] = "0.1"  # Medium packet loss
        self.server_process = subprocess.Popen(
            ["python", self.server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,  # To ensure output is returned as strings, not bytes
            bufsize=1  # Line-buffered output for real-time processing
        )
        time.sleep(1)  # Wait for the server to start

    def tearDown(self):
        self.server_process.terminate()
        stdout, stderr = self.server_process.communicate()
        print("\nServer Output:\n", stdout)
        print("\nServer Errors:\n", stderr)
        self.server_process.wait()

    def test_variable_rtt(self):
        client_path = os.path.join(os.path.dirname(__file__), "../client.py")
        try:
            client_process = subprocess.Popen(
                ["python", client_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  # To process output as strings
                bufsize=1  # Line-buffered output for real-time reading
            )

            # Read output line by line in real-time
            for line in client_process.stdout:
                print(line.strip())  # Print the line as it appears
                if "High RTT detected" in line:
                    print("Detected high RTT during test execution.")
                if "Reducing window size" in line:
                    print("Window size is being reduced during the test.")

            client_process.stdout.close()
            client_process.wait(timeout=35)
        except subprocess.TimeoutExpired:
            client_process.kill()
            self.fail("Client process timed out.")
        except Exception as e:
            client_process.kill()
            raise e

        print("Test completed successfully!")


if __name__ == "__main__":
    unittest.main()
