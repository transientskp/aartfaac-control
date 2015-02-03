import socket

class Connection:
    TIMEOUT = 5
    OK = "OK"
    NOK = "NOK"

    def __init__(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr, port):
        # Connect the socket to the port where the server is listening
        server_address = (addr, port)
        print "Connecting to %s port %s" % server_address
        try:
            self.sock.settimeout(Connection.TIMEOUT)
            self.sock.connect(server_address)
            self.sock.settimeout(None)
        except socket.error:
            return Connection.NOK
        return Connection.OK

    def send(self, cmd):
        response = Connection.NOK
        try:
            self.sock.sendall(cmd)
            self.sock.settimeout(Connection.TIMEOUT)
            response = self.sock.recv(1024).strip()
            self.sock.settimeout(None)
        except IOError:
            return Connection.NOK

        return str(response)

    def close(self):
        self.sock.close()

