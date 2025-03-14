import unittest
import subprocess
import os
import time


class TestHighPacketLoss(unittest.TestCase):
    def setUp(self):
        self.server_path = os.path.join(os.path.dirname(__file__), "../server.py")
        env = os.environ.copy()
        env["PACKET_LOSS_PROB"] = "0.3"
        self.server_process = subprocess.Popen(
            ["python", self.server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1  # Line-buffered output
        )
        time.sleep(1)  # Wait for the server to start

    def tearDown(self):
        self.server_process.terminate()
        stdout, stderr = self.server_process.communicate()
        print("\nServer Output:\n", stdout)
        print("\nServer Errors:\n", stderr)
        self.server_process.wait()

    def test_high_packet_loss(self):
        client_path = os.path.join(os.path.dirname(__file__), "../client.py")
        try:
            client_process = subprocess.Popen(
                ["python", client_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line-buffered output
            )

            # Process client output in real-time
            client_output = []
            for line in iter(client_process.stdout.readline, ''):
                print(line.strip())  # Real-time output
                client_output.append(line.strip())  # Save output for later assertions

            client_process.stdout.close()
            client_process.wait(timeout=35)
        except subprocess.TimeoutExpired:
            client_process.kill()
            self.fail("Client process timed out.")
        except Exception as e:
            client_process.kill()
            raise e

        # Assertions to ensure correct behavior
        output = "\n".join(client_output)  # Combine output lines for assertion
        self.assertIn("Packet lost", output, "Client should detect packet loss.")
        self.assertIn("Fast Recovery", output, "Client should enter Fast Recovery mode.")
        self.assertLess(
            output.count("Packet lost"), 50,
            "Too many packets lost in high packet loss scenario."
        )
        self.assertIn("Current window size", output, "Window size updates are missing.")

        print("TestHighPacketLoss: Test passed successfully!")


if __name__ == "__main__":
    unittest.main()
