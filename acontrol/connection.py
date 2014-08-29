import os
import paramiko

class Connection(object):
  def __init__(self, host, dryrun=False):
    self.dryrun = dryrun
    self.host = {'hostname': host}

    if not dryrun:
      self.config = paramiko.SSHConfig()
      self.config.parse(open(os.path.expanduser('~/.ssh/config')))
      self.host = self.config.lookup(host)
      self.client = paramiko.SSHClient()
      self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      self.client.load_system_host_keys()

      if not self.host:
        self.host = {'hostname': host}
        
      self.client.connect(**self.host)
      self.transport = self.client.get_transport()
      self.channels = {}

  def start_program(self, cmd):
    print "Executing: %s on %s" % (cmd, self.host['hostname'])
    if not self.dryrun:
      self.channels[cmd] = self.transport.open_session()
      self.channels[cmd].get_pty()
      self.channels[cmd].exec_command(cmd)

  def stop_program(self, cmd):
    print "Stopping: %s on %s" % (cmd, self.host['hostname'])
    if self.channels.has_key(cmd):
      self.channels[cmd].close()
      del self.channels[cmd]
