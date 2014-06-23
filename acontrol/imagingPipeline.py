from acontrol.connection import Connection

GIT_SHA1 = "dcd9c05" # $(git log -1 --format="%h")
CMD = "docker run -v /data:/data:rw --expose %d aartfaac/imaging:%d " \
      "start_pipeline --monitor-port=%d --server-host=%s --server-port=%d " \
      "--casa /data/%s"


class ImagingPipeline(Connection):

    def __init__(self, host):
        super(ImagingPipeline, self).__init__(host)
        self.mon_port = 4200
        self.commands = []

    def start_pipelines(self, num, server_addr, server_port, obs):
        for i in range(0, num):
            cmd = CMD % (self.mon_port+i, GIT_SHA1, self.mon_port+i, server_addr, server_port, obs.start)
            self.commands.append(cmd)
            self.start_program(cmd)

    def stop_pipelines(self):
        for cmd in self.commands:
            self.stop_program(cmd)
