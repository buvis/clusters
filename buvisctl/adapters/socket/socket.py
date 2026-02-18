import socket
import time

from adapters.response import AdapterResponse


class SocketAdapter:

    def __init__(self):
        pass

    def is_open(self, ip, port, timeout=600):
        sleep_count = 0

        while True:
            try:
                tester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tester.connect((ip, port))

                return AdapterResponse()
            except OSError as e:
                time.sleep(5)
                sleep_count = sleep_count + 1

                if sleep_count > timeout / 5:
                    return AdapterResponse(code=504, message=e)
            finally:
                tester.close()
