import os
import paramiko

class Connection(object):
    def __init__(self, host, dryrun=False):
        self.dryrun = dryrun
        self.config = paramiko.SSHConfig()
        self.config.parse(open('~/.ssh/config'))
        self.host = self.config.lookup(host)
        self.transport = None

        if not self.host:
            raise IOError("Hostname `%s' not defined in %s" % (host, os.path.expanduser('~/.ssh/config')))

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.channels = {}


    def connect(self):
        print "Connecting: %s@%s" % (self.host['user'], self.host['hostname'])
        for k in self.channels.keys():
            del self.channels[k]

        if not self.dryrun:
            self.client.connect(self.host['hostname'], 22, self.host['user'])
            self.transport = self.client.get_transport()


    def start_program(self, cmd):
        if not self.transport or not self.transport.is_active():
            self.connect()

        print "Executing: %s" % (cmd)
        if not self.dryrun and not self.channels.has_key(cmd):
            self.channels[cmd] = self.transport.open_session()
            self.channels[cmd].get_pty()
            self.channels[cmd].exec_command(cmd)


    def stop_program(self, cmd):
        print "Stopping: %s on %s" % (cmd, self.host['hostname'])
        if not self.dryrun and self.channels.has_key(cmd):
            self.channels[cmd].close()
            del self.channels[cmd]
