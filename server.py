import socket
import threading

class Server:
    def __init__(self, address, port, max_connections):
        print("Setting up server...")
        self.address = address
        self.port = port
        self.max_connections = max_connections
        self.active_connections = 0

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen(max_connections)

        self.clients = []

    def start(self):
        print("Starting server...")
        while True:
            client, client_address = self.socket.accept()
            try:
                print("------------------------------------------------------------------------")
                print("Client {0}:{1} connected.".format(client_address[0], client_address[1]))
                self.active_connections += 1
                print("Current connections: {}".format(str(self.active_connections)))
            except:
                pass
            client_handler = threading.Thread(target=self.handle_client, args=(client, client_address))
            client_handler.start()

    def end(self):
        print("Stopping server...")
        self.socket.close()

    def handle_client(self, connection, client_info):
        client_nickname = "guest_" + str(self.active_connections)
        self.clients.append(connection)

        client_ip, client_port = client_info
        connection.send(b"Welcome, type anything...\n")

        while True:
            try:
                request = connection.recv(1024)
            except:
                break

            received = request.decode('UTF-8').strip()

            if "/setnickname" in received:
                new_nickname = self.set_client_nickname(received)
                if new_nickname:
                    client_nickname = self.set_client_nickname(received)
                else:
                    connection.send(b"Something went wrong...\n")
            elif received == '/online':
                self.server_message("There are currently {} user(s) connected\n".format(self.active_connections))
            elif received == '/exit':
                break

            self.global_message(client_nickname, received)

        connection.close()
        self.active_connections -= 1
        print("Client {0}:{1} left. Current connections: {2}".format(client_ip, client_port, self.active_connections))

    def server_message(self, msg):
        for client in self.clients:
            client.send(msg.encode())

    def global_message(self, nickname, message):
        msg = "{0} wrote: {1}\n".format(nickname, message)
        if self.active_connections > 1:
            self.server_message(msg)
        else:
            self.clients[0].send(b"You're the only one here right now\n")
            print("There are no clients")

    def set_client_nickname(self, user_command):
        try:
            return user_command.split()[1]
        except:
            return None

