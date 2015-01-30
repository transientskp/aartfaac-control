#!/usr/bin/python
# Generic Python client to control the various processing blocks of the AARTFAAC
# pipeline. 
# Functionality:
#   - Blocks on a TCP listen(), waiting for a command server to connect
# 	  to a known port. 
# 	- Spawn a thread to service the command.
#   - Thread receives commands over TCP from the server, executes them,
#	  reports back status on the same open connection.
# pep/29Jan15

import sys;
import socket;
import thread;
import time;

class cmdClient:
	_cmdport = 44000; # Port on which command server should connect.

	def __init__ (self):
		self._cmd = 'READY';
		self._fid = socket.socket (socket.AF_INET, socket.SOCK_STREAM);
		print '--> Binding on port ', self._cmdport;
		self._fid.bind( ('', self._cmdport) );

	def run (self):
		print 'In run'
		while (self._cmd is not 'QUIT'):
			self._fid.listen(1); # Blocking wait
			self._servsock, self._servaddr = self._fid.accept();
			print '--> Received connection from ', self._servaddr;
			thread.start_new_thread (threadhdlr, (self._servsock, self._servaddr));

	def threadhdlr (self):
		line = self._servsock.recv (1024);
		print 'Client sent:' ,line;
		self._status = 'OK';
		print 'We send:', self._status;
		self._servsock.send(self._status);

	def __del__(self):
		# Send termination signal to all threads
		self._fid.close();	
	

# Object to handle teh startup of a pelican server, including generating a 
# status on whether startup was successful, based on parsing the stdout.
class pelicanServerCmdClient (cmdClient):

	def __init__ (self):
		cmdClient.__init__(self);

if __name__ == '__main__':
	cl = cmdClient();
	cl.run();	

