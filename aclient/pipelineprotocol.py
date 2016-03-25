import os
import signal
import multiprocessing

from twisted.internet import reactor

from aclient.controlprotocol import ControlProtocol
from aclient.writeprocessprotocol import WriteProcessProtocol

class PipelineProtocol(ControlProtocol):
    process = [None] * multiprocessing.cpu_count()
    def start(self, argv):
        count = 0
        cmd = ["start_pipeline.py"] + argv.split()
        for i,p in enumerate(PipelineProtocol.process):
            if not p or not p.is_running:
                print "Starting pipeline with args: {}".format(argv)
                PipelineProtocol.process[i] = WriteProcessProtocol(cmd[0], self.factory.config['logdir'])
                reactor.spawnProcess(PipelineProtocol.process[i], cmd[0], cmd, env=os.environ)
                count += 1
            else:
                print "Error: Pipeline is already running, stop first"
        if count > 0:
            self.sendSuccess()
        else:
            self.sendFailure()

    def stop(self):
        for p in PipelineProtocol.process:
            try:
                if p and p.is_running:
                    p.transport.signalProcess(signal.SIGTERM)
                else:
                    print "Error: Process already exited"
            except OSError as e:
                print "Error: Unable to kill {}".format(p.pid)
        self.sendSuccess()
