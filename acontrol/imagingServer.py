from acontrol.connection import Connection

GIT_SHA1 = "UNDEFINED"
CMD = "docker run -d --expose %d -p %d:%d aartfaac/imaging:%d " \
      "start_server.py --stream 64 %f %f 1-63"


class ImagingServer(Connection):

    def __init__(self, host):
        super(ImagingServer, self).__init__(host)
        self.port_in = 4100
        self.port_out = 2000
        self.server_cmd = None

    def start_server(self, obs):
        self.server_cmd = CMD % (self.port_in, self.port_out, self.port_out, GIT_SHA1, obs.start_freq, obs.chan_width)
        self.start_program(self.server_cmd)

    def stop_server(self):
        self.stop_program(self.server_cmd)
