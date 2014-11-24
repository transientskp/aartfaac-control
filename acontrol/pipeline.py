from acontrol.connection import Connection

GIT_SHA1 = "3d1d52a" # $(git log -1 --format="%h")
CMD = "docker run --expose %d -v /data:/data:rw aartfaac:%s start_pipeline.py /data/$(date +%y%m%d-%H%M) --nthreads=63 --server-host=%s --server-port=%d --casa --monitor-port=%d --antenna-positions=/usr/local/share/aartfaac/antennasets/%s.dat"

class ImagingPipeline(Connection):

    def __init__(self, host, dryrun):
        super(ImagingPipeline, self).__init__(host, dryrun)
        self.mon_port = 4200
        self.commands = []

    def start(self, num, server_addr, server_port, obs):
        for i in range(0, num):
            cmd = CMD % (self.mon_port+i, GIT_SHA1, obs.start, server_addr, server_port, self.mon_port+i, obs.antenna_set.lower())
            self.commands.append(cmd)
            self.start_program(cmd)

    def stop(self):
        for cmd in self.commands:
            self.stop_program(cmd)
        del self.commands[:]
