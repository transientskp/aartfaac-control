from acontrol.connection import Connection

GIT_SHA1 = "9f63600" # $(git log -1 --format="%h")
CMD = "docker --expose %d:%d run -v /data:/data:rw aartfaac:%s start_pipeline.py /data/%s " \
      "--server-host=%s --server-port=%d --casa --monitor-port=%d " \
      "--antenna-positions=/usr/local/share/aartfaac/antennasets/%s.dat"

class ImagingPipeline(Connection):

    def __init__(self, host):
        super(ImagingPipeline, self).__init__(host)
        self.mon_port = 4200
        self.commands = []

    def start_pipelines(self, num, server_addr, server_port, obs):
        for i in range(0, num):
            cmd = CMD % (self.mon_port+i, self.mon_port+i, GIT_SHA1, obs.start, server_addr, server_port, self.mon_port+i, obs.antenna_set.lower())
            self.commands.append(cmd)
            self.start_program(cmd)

    def stop_pipelines(self):
        for cmd in self.commands:
            self.stop_program(cmd)
