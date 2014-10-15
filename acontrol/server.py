from acontrol.connection import Connection

GIT_SHA1 = "9f63600" # $(git log -1 --format="%h")
CMD = "docker run -p %d:%d -p %d:%d aartfaac:%s " \
      "start_server.py --stream 63 %f %f 32-32"


class ImagingServer(Connection):

    def __init__(self, host, dryrun):
        super(ImagingServer, self).__init__(host, dryrun)
        self.port_in = 4100
        self.port_out = 2000
        self.cmd = None

    def start(self, obs):
        self.cmd = CMD % (self.port_in, self.port_in, self.port_out, self.port_out, GIT_SHA1, obs.start_freq, obs.chan_width)
        self.start_program(self.cmd)

    def stop(self):
        self.stop_program(self.cmd)
