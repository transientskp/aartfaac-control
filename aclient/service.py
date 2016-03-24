import os

from twisted.internet import reactor
from twisted.internet import protocol
from twisted.python import usage
from twisted.python import log
from twisted.application import internet

from aclient.serverprotocol import ServerProtocol

class Options(usage.Options):
    optParameters = [
        ["port", None, 45000, "Port to listen on for incomming connections"],
        ["program", None, None, "Program to start, one of {server, atv, pipeline, correlator}"]
    ]


def makeService(config):
    protocols = {"server":ServerProtocol}
    factory = protocol.ServerFactory()
    factory.protocol = protocols[config['program'].lower()]
    service = internet.TCPServer(config['port'], factory)
    return service

