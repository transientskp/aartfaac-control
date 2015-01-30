import socket

class Connection:
    OK = "OK"
    NOK = "NOK"

    def __init__(self, addr, port):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = (addr, port)
        print "Connecting to %s port %s" % server_address
        self.sock.connect(server_address)

    def send(self, cmd):
        response = Connection.NOK
        try:
            self.sock.sendall(cmd)
            response = self.sock.recv(1024)
        finally:
            self.sock.close()

        return str(response)

    def close():
        self.sock.close()

