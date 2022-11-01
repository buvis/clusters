import socket
import time


def wait_for_connection(ip, port, timeout=600):
    sleep_count = 0

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.close()

            return True
        except socket.error:
            time.sleep(5)
            sleep_count = sleep_count + 1

            if sleep_count > timeout / 5:
                return False
