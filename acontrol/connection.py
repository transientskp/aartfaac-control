import os
import paramiko

class Connection(object):
  def __init__(self, host):
    self.config = paramiko.SSHConfig()
    self.config.parse(open(os.path.expanduser('~/.ssh/config')))
    self.host = self.config.lookup(host)
    self.client = paramiko.SSHClient()
    self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.client.load_system_host_keys()

    proxy = None
    if self.host.has_key('proxycommand'):
      proxy = paramiko.ProxyCommand(self.host['proxycommand'])
    self.client.connect(self.host['hostname'], sock=proxy)
    self.transport = self.client.get_transport()
    self.channels = {}

  def start_program(self, cmd):
    print "Executing: %s" % (cmd)
    # FIXME !!!
    return
    self.channels[cmd] = self.transport.open_session()
    self.channels[cmd].get_pty()
    self.channels[cmd].exec_command(cmd)

  def stop_program(self, cmd):
    if self.channels.has_key(cmd):
      self.channels[cmd].close()
      del self.channels[cmd]