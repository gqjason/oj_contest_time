import socket
import threading

PORT = 65432  # 你可以换成任意未占用端口
HOST = '127.0.0.1'

class InstanceWakeupServer:
    def __init__(self, on_show_callback):
        self.on_show_callback = on_show_callback
        self.running = True
        self.thread = threading.Thread(target=self.run_server, daemon=True)
        self.thread.start()

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((HOST, PORT))
                s.listen(1)
                while self.running:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(1024).decode()
                        if data == 'show':
                            self.on_show_callback()
            except OSError:
                # 端口已占用，说明已有实例在运行
                pass

def notify_existing_instance():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'show')
    except:
        pass
