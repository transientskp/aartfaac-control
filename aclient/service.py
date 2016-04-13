import os
import sys

from twisted.python import usage
from twisted.application import internet

from aclient.correlatorprotocol import CorrelatorProtocol
from aclient.serverprotocol import ServerProtocol
from aclient.pipelineprotocol import PipelineProtocol
from aclient.atvprotocol import AtvProtocol
from aclient.controlprotocol import ControlFactory

PROTOCOLS = {
    "server":ServerProtocol, 
    "pipeline":PipelineProtocol, 
    "correlator":CorrelatorProtocol, 
    "atv":AtvProtocol
}



class Options(usage.Options):
    optParameters = [
        ["port", None, 45000, "Port to listen on for incomming connections"],
        ["program", None, None, "Program to start, one of {%s}" % (", ".join(PROTOCOLS.keys()))],
        ["logdir", None, "/tmp/aclient", "Program logfiles directory"]
    ]


def makeService(config):
    if config['program'] not in PROTOCOLS.keys():
        raise Exception("'{}' not a valid program\n".format(config['program']))

    if not os.path.exists(config['logdir']):
        os.makedirs(config['logdir'])

    factory = ControlFactory(config)
    factory.protocol = PROTOCOLS[config['program'].lower()]
    service = internet.TCPServer(config['port'], factory)
    return service

