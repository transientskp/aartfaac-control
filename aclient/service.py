import os
import sys

from twisted.internet import reactor
from twisted.internet import protocol
from twisted.python import usage
from twisted.python import log
from twisted.application import internet

from aclient.correlatorprotocol import CorrelatorProtocol
from aclient.serverprotocol import ServerProtocol
from aclient.pipelineprotocol import PipelineProtocol
from aclient.atvprotocol import AtvProtocol

PROTOCOLS = {
    "server":ServerProtocol, 
    "pipeline":PipelineProtocol, 
    "correlator":CorrelatorProtocol, 
    "atv":AtvProtocol
}



class ProgramFactory(protocol.ServerFactory):
    """Our own program factory that allows us to pass config"""
    def __init__(self, config):
        self.config = config


class Options(usage.Options):
    optParameters = [
        ["port", None, 45000, "Port to listen on for incomming connections"],
        ["program", None, None, "Program to start, one of {{{}}}".format(", ".join(PROTOCOLS.keys()))],
        ["logdir", None, "/tmp/aclient", "Program logfiles directory"]
    ]


def makeService(config):
    if config['program'] not in PROTOCOLS.keys():
        sys.stderr.write("Error: '{}' not a valid program\n".format(config['program']))
        sys.exit(1)

    if not os.path.exists(config['logdir']):
        os.makedirs(config['logdir'])
        print "Created directory '{}' for logging programs".format(config['logdir'])

    factory = ProgramFactory(config)
    factory.protocol = PROTOCOLS[config['program'].lower()]
    service = internet.TCPServer(config['port'], factory)
    return service

