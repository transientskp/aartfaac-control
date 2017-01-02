import os
import sys

from twisted.python import usage
from twisted.application import internet

from aclient.controlprotocol import ControlFactory

PROGRAMS = {
    "pipeline": {
        "cmd":['aartfaac-calibration'],
        "env":os.environ
    },

    "correlator": {
        "cmd":['numactl', '-i',  '0-1', '/home/romein/projects/Triple-A/AARTFAAC/installed/AARTFAAC'],
        "env":{'DISPLAY':':0', 'GPU_FORCE_64BIT_PTR':'1', 'PLATFORM':'AMD Accelerated Parallel Processing', 'TYPE':'GPU'}
    },

<<<<<<< HEAD
    "firmware": {
        "cmd":['/home/huizinga/SVN/Aartfaac/trunk/Software/sh/load_aartfaac_12_images.sh', '16'],
=======
    "atv": {
        "cmd":['twistd', '-l', 'atv.log', 'atv'],
>>>>>>> 91a97fe... Add atv to client
        "env":os.environ
    }
}


class Options(usage.Options):
    optParameters = [
        ["port", None, 45000, "Port to listen on for incomming connections"],
        ["program", None, None, "Program in {%s}" % (", ".join(PROGRAMS.keys()))],
        ["logdir", None, "/tmp/aclient", "Program logfiles directory"]
    ]


def makeService(config):
    if config['program'] not in PROGRAMS.keys():
        raise Exception("'{}' not a valid program\n".format(config['program']))

    if not os.path.exists(config['logdir']):
        os.makedirs(config['logdir'])

    program = PROGRAMS[config['program'].lower()]
    factory = ControlFactory(config, program['cmd'], program['env'])
    service = internet.TCPServer(int(config['port']), factory)
    return service

