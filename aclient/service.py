import os
import sys

from twisted.python import usage
from twisted.application import internet

from aclient.controlprotocol import ControlFactory

PROGRAMS = {
    "atv": {
        "cmd":['aartfaac-tv'],
        "env":os.environ
    },
    "imager": {
        "cmd":['aartfaac-imaging'],
        "env":os.environ
    },
    "pipeline": {
        "cmd":['aartfaac-calibration'],
        "env":os.environ
    },
    "correlator": {
        "cmd":['/home/romein/projects/Triple-A/AARTFAAC/installed/AARTFAAC'],
        "env":{'DISPLAY':':0', 'GPU_FORCE_64BIT_PTR':'1', 'PLATFORM':'AMD Accelerated Parallel Processing', 'TYPE':'GPU'}
    },
    "firmware": {
        "cmd":['/home/huizinga/SVN/Aartfaac/trunk/Software/sh/load_aartfaac_12_images.sh', '16'],
        "env":os.environ
    },
    "atv": {
        "cmd":['twistd', '-n', '-l', '-', 'atv'],
        "env":os.environ
    }
}


class Options(usage.Options):
    optParameters = [
        ["port", None, 45000, "Port to listen on for incomming connections"],
        ["program", None, None, "Program in {%s}" % (", ".join(PROGRAMS.keys()))],
        ["numactl", None, "", "numactl arglist, e.g. '-C 0-8 -i 0-1'"],
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

