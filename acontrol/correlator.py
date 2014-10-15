from acontrol.connection import Connection

CMD = "startgpu.sh"

class Correlator(Connection):

    def __init__(self, host, dryrun):
        super(Correlator, self).__init__(host, dryrun)
        self.cmd = None

    def start(self, obs):
        self.cmd = CMD
        self.start_program(self.cmd)

    def stop(self): 
        self.stop_program(self.cmd)
