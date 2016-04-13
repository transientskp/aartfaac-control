import textwrap
import shutil
import tempfile
import os

from twisted.trial import unittest
from twisted.python import usage
from twisted.internet import reactor
from twisted.test import proto_helpers

from acontrol.controlprotocol import ControlProtocol, ControlFactory
from acontrol.test.example_parset import EXAMPLE_PARSET
from acontrol.test.example_config import TestWithConfig
from acontrol.configuration import Configuration
from acontrol.observation import Observation
from acontrol.service import *
from acontrol.mailnotify import *

LOCAL_CONFIG = """
{
  "starttime": "2016-03-07 04:12:47",
  "lba": {
    "modes": ["lba_inner", "lba_outer"],
    "subbands": [
      295,
      296,
      297,
      298,
      299,
      300,
      301,
      302
    ],
    "channels": [
      0,
      62
    ],
    "flagged": [
      2,
      4,
      128
    ]
  },
  "hba": {
    
  },
  "programs": {
    "atv": {
      "address": "127.0.0.1:45000",
      "subband": 299,
      "args": {
        "output": "\/data\/atv",
        "snapshot": "\/var\/www",
        "port": 5000
      }
    },
    "correlator": {
      "address": "127.0.0.1:46000",
      "args": {
        "b": 16
      }
    },
    "server": {
      "address": "127.0.0.1:47000",
      "args": {
        "buffer-max-size": 64424509440,
        "input-host": "10.195.100.3"
      }
    },
    "pipeline": {
      "address": [
        "127.0.0.1:48000",
        "127.0.0.1:48000",
        "127.0.0.1:48000"
      ],
      "args": {
        "ant-sigma": 4,
        "vis-sigma": 3
      }
    }
  }
}
"""
LOCAL_CONFIG = textwrap.dedent(LOCAL_CONFIG).strip()

class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_dir = tempfile.mkdtemp()
        self.lof_dir = tempfile.mkdtemp()
        self.parset = tempfile.NamedTemporaryFile(mode='w')
        self.parset.write(EXAMPLE_PARSET)
        self.parset.seek(0)
        self.obs = Observation(self.parset.name)
        self.mailfile = tempfile.NamedTemporaryFile(mode='w')
        self.mailfile.write('none@none.com\n')
        self.mailfile.seek(0)

        self.config = Options()
        self.config.parseOptions(['--maillist',self.mailfile.name,'--lofar-dir',self.lof_dir, '--config-dir',self.cfg_dir])

    def _make_service(self, options):
        self.config.parseOptions(options)
        return makeService(self.config)

    def test_make_service(self):
        service = self._make_service(['--maillist',self.mailfile.name,'--lofar-dir',self.lof_dir, '--config-dir',self.cfg_dir])
        for service_name in ("LOFAR Parset Notifier", "AARTFAAC Config Notifier", "Worker"):
            self.assertTrue(service.namedServices.has_key(service_name))

    def test_process_obs(self):
        
        def conn_pass(name, host, port, argv, start):
            conn_pass.counter += 1
            d = defer.Deferred()
            d.callback("success")
            return d
        conn_pass.counter = 0

        email = MailNotify(self.config['maillist'], True)
        ws = WorkerService(self.config, email, LOCAL_CONFIG)
        ws.startService()
        ws.processObservation(self.obs, connector=conn_pass)
        ws.stopService()
        self.assertEqual(conn_pass.counter, 6)

    def tearDown(self):
        for call in reactor.getDelayedCalls():
            call.cancel()
        shutil.rmtree(self.cfg_dir)
        shutil.rmtree(self.lof_dir)
