import socket
import threading
import logging
from datetime import datetime

# Thread class to handle each client
class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address

    def run(self):
        logging.info(f"[CONNECTED] Client from {self.address}")
        try:
            while True:
                data = b''
                while not data.endswith(b'\r\n'):
                    chunk = self.connection.recv(32)
                    if not chunk:
                        logging.warning(f"[DISCONNECTED] Client {self.address} closed the connection.")
                        return
                    data += chunk

                decoded_data = data.decode('utf-8').strip()
                logging.info(f"[RECEIVED from {self.address}] {repr(decoded_data)}")

                if decoded_data.upper() == 'TIME':
                    now = datetime.now()
                    current_time = now.strftime('%H:%M:%S')
                    response = f"JAM {current_time}\r\n"
                    self.connection.sendall(response.encode('utf-8'))
                elif decoded_data.upper() == 'QUIT':
                    logging.info(f"[QUIT] Client {self.address} requested to quit.")
                    break
                else:
                    response = "INVALID REQUEST\r\n"
                    self.connection.sendall(response.encode('utf-8'))
        except Exception as e:
            logging.error(f"[ERROR] Handling client {self.address}: {e}")
        finally:
            self.connection.close()
            logging.info(f"[CLOSED] Connection with {self.address}")

# Server class that accepts incoming connections
class Server(threading.Thread):
    def __init__(self, port=45000):
        threading.Thread.__init__(self)
        self.the_clients = []
        self.port = port
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(5)
        logging.info(f"[STARTED] Time server running on port {self.port}...")

        while True:
            connection, client_address = self.my_socket.accept()
            client_thread = ProcessTheClient(connection, client_address)
            client_thread.start()
            self.the_clients.append(client_thread)

# Entry point
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    server = Server()
    server.start()

if __name__ == "__main__":
    main()
