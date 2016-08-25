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
from acontrol.test.example_config import EXAMPLE_CONFIG
from acontrol.configuration import Configuration
from acontrol.observation import Observation
from acontrol.service import *
from acontrol.mailnotify import *

class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_dir = tempfile.mkdtemp()
        self.lof_dir = tempfile.mkdtemp()
        self.parset = tempfile.NamedTemporaryFile(mode='w')
        self.parset.write(EXAMPLE_PARSET)
        self.parset.seek(0)
        self.obs = Observation(self.parset.name)
        self.config = Options()
        self.config.parseOptions(['--lofar-dir',self.lof_dir, '--config-dir',self.cfg_dir])


    def _make_service(self, options):
        self.config.parseOptions(options)
        return makeService(self.config)


    def test_make_service(self):
        service = self._make_service(['--lofar-dir',self.lof_dir, '--config-dir',self.cfg_dir])
        for service_name in ("LOFAR Parset Notifier", "AARTFAAC Config Notifier", "Worker"):
            self.assertTrue(service.namedServices.has_key(service_name))


    def test_success_chain(self):
        
        def conn_pass(name, host, port, argv):
            conn_pass.counter += 1
            d = defer.Deferred()
            d.callback("success")
            return d
        conn_pass.counter = 0

        email = MailNotify(True)
        email.updatelist(["none@uva.nl"])
        ws = WorkerService(self.config, email, EXAMPLE_CONFIG)
        ws.startService()
        ws.processObservation(self.obs, connector=conn_pass)
        ws.stopService()
        self.assertEqual(conn_pass.counter, 18)


    def test_fail_chain(self):
        
        def conn_fail(name, host, port, argv):
            d = defer.Deferred()
            if "ais002" in name:
                d.errback(Exception("fail"))
            else:
                conn_fail.counter += 1
                d.callback("success")
            return d
        conn_fail.counter = 0

        email = MailNotify(True)
        email.updatelist(["none@uva.nl"])
        ws = WorkerService(self.config, email, EXAMPLE_CONFIG)
        ws.startService()
        ws.processObservation(self.obs, connector=conn_fail)
        ws.stopService()
        self.assertEqual(conn_fail.counter, 15)
        

    def test_success_chain_minimal(self):
        
        def conn_fail(name, host, port, argv):
            d = defer.Deferred()
            if name in "ais002-1 agc001":
                conn_fail.counter += 1
                d.callback("success")
            else:
                d.errback(Exception("fail"))
            return d
        conn_fail.counter = 0

        email = MailNotify(True)
        email.updatelist(["none@uva.nl"])
        ws = WorkerService(self.config, email, EXAMPLE_CONFIG)
        ws.startService()
        ws.processObservation(self.obs, connector=conn_fail)
        ws.stopService()
        self.assertEqual(conn_fail.counter, 2)


    def test_stop(self):
        def conn(name, host, port, argv):
            d = defer.Deferred()
            d.callback("success")
            conn.counter += 1
            return d
        conn.counter = 0

        email = MailNotify(True)
        email.updatelist(["none@uva.nl"])
        ws = WorkerService(self.config, email, EXAMPLE_CONFIG)
        ws.startService()
        ws.endObservation(self.obs, connector=conn)
        ws.stopService()
        self.assertEqual(conn.counter, 18)





    def tearDown(self):
        for call in reactor.getDelayedCalls():
            call.cancel()
        shutil.rmtree(self.cfg_dir)
        shutil.rmtree(self.lof_dir)
