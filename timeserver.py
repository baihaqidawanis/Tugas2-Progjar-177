import socket
import threading
import logging
from datetime import datetime

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, client_addr):
        super().__init__()
        self.client_socket = client_socket
        self.client_addr = client_addr

    def recv_until_crlf(self):
        """Receive data until CRLF (\r\n) is found."""
        data = b''
        while not data.endswith(b'\r\n'):
            packet = self.client_socket.recv(32)
            if not packet:
                return None
            data += packet
        return data.decode('utf-8').strip()

    def send_response(self, message):
        self.client_socket.sendall(message.encode('utf-8'))

    def handle_command(self, command):
        cmd_upper = command.upper()
        if cmd_upper == "TIME":
            current_time = datetime.now().strftime("%H:%M:%S")
            response = f"JAM {current_time}\r\n"
            self.send_response(response)
        elif cmd_upper == "QUIT":
            logging.info(f"[QUIT] Client {self.client_addr} requested to disconnect.")
            return False
        else:
            self.send_response("INVALID REQUEST\r\n")
        return True

    def run(self):
        logging.info(f"[CONNECTED] Client connected from {self.client_addr}")
        try:
            while True:
                msg = self.recv_until_crlf()
                if msg is None:
                    logging.warning(f"[DISCONNECTED] Client {self.client_addr} closed the connection unexpectedly.")
                    break
                logging.info(f"[RECEIVED] From {self.client_addr}: {repr(msg)}")
                if not self.handle_command(msg):
                    break
        except Exception as err:
            logging.error(f"[ERROR] Exception handling client {self.client_addr}: {err}")
        finally:
            self.client_socket.close()
            logging.info(f"[CLOSED] Connection closed with {self.client_addr}")

class TimeServer(threading.Thread):
    def __init__(self, host='0.0.0.0', port=45000):
        super().__init__()
        self.host = host
        self.port = port
        self.client_threads = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"[STARTED] Time server listening on {self.host}:{self.port}")
        while True:
            client_sock, client_addr = self.server_socket.accept()
            client_thread = ClientHandler(client_sock, client_addr)
            client_thread.start()
            self.client_threads.append(client_thread)

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    server = TimeServer()
    server.start()

if __name__ == "__main__":
    main()
