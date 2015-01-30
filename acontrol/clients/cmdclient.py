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
import subprocess;
import time;
import argparse;

class cmdClient:
	_cmdport = 45000; # Port on which command server should connect.

	def __init__ (self):
		self._cmd = 'READY';
		self._fid = socket.socket (socket.AF_INET, socket.SOCK_STREAM);
		print '--> Binding on port ', self._cmdport;
		self._fid.bind( ('', self._cmdport) );
		self._runcmd = ['date'];

	def run (self):
		print 'In run'
		while (self._cmd != 'QUIT'):
			self._fid.listen(1); # Blocking wait
			self._servsock, self._servaddr = self._fid.accept();
			print '--> Received connection from ', self._servaddr, 'cmd', self._cmd, self._cmd != 'QUIT', type (self._cmd);
			thread.start_new_thread (self.threadhdlr,());

	def threadhdlr (self):
		self._cmd = self._servsock.recv (1024);
		self._status = 'OK';
		if self._cmd is 'START':
			try:
				cmdout = subprocess.check_call (self._runcmd, shell=True);
			except CalledProcessError:
				print 'Error in executing process!';
				self._status = 'NOK';

		elif self._cmd is 'STOP':
#			try:
#				cmdout = subprocess.check_call (self._runcmd, shell=True);
#			except CalledProcessError:
#				print 'Error in executing process!';
			self._status = 'OK';

		print 'We send:', self._status;
		self._servsock.send(self._status);

	# Method to show the history of commands received by this cmdclient
	# TODO
	def showcmdhist (self):
		return False;

	def __del__(self):
		# Send termination signal to all threads
		# TODO.
		self._fid.close();	
	

# Object to handle the startup of a pelican server, including generating a 
# status on whether startup was successful, based on parsing the stdout.
class pelicanServerCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = ['ls -l'];

class pipelineCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = ['ls -l'];

class gpuCorrCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = ['ls -l'];


class lcuafaacCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = ['ls -l'];


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--procblk", help="Specify which processing block cmdclient controls", default='gpucorr');
	client = parser.parse_args();

	if client.procblk == 'gpucorr':
		cl = gpuCorrCmdClient ();

	elif client.procblk == 'lcu':
		cl = lcuafaacCmdClient();	

	elif client.procblk == 'pipe':
		cl = pipelineCmdClient();

	elif client.procblk == 'pelican':
		cl = pelicanserverCmdClient();

	else:
		print '### Unknown processing block!';
		sys.exit (-1);

	cl.run();	

