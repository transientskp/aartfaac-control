import threading
import paramiko

from acontrol.connection import Connection

class Imaging(Connection):
  def __init__(self):
    super('localhost')
    self.cmd = 'tail -f .bashrc'

  def start_server(self):
    super(Imaging, self).start_program(self.cmd)

  def stop_server(self):
    super(Imaging, self).stop_program(self.cmd)
