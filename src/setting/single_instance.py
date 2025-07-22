# single_instance.py
import socket

class SingleInstance:
    def __init__(self, port=56789):
        self.port = port
        self.lock_socket = None

    def is_running(self):
        """判断是否已有程序实例运行"""
        self.lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.lock_socket.bind(("127.0.0.1", self.port))
        except socket.error:
            return True
        return False
