#!/usr/bin/python
# Generic Python client to control the various processing blocks of the AARTFAAC
# pipeline. 
# Functionality:
#   - Blocks on a TCP listen(), waiting for a command server to connect
# 	  to a known port. 
# 	- Spawn a thread to service an incoming connection.
#   - Thread receives commands over TCP from the server, executes them,
#	  reports back status on the same open connection.
#   - Command protocol: text based, space separated fields.
#     Field 1: Protocol version
#     Field 2: Command to client
#     Field 3: Argument list for command to run on remote processing block.
#   
#   - Security: The command to run is hardcoded in the program. Only the command arguments 
#	 are received over the socket. These can be encrypted in future.     
# TODO:
#   - Parse output, generate OK/NOK correctly
#   - Figure out a nice way to stop the process.
# pep/29Jan15

import sys;
import socket;
import thread;
import subprocess;
import time;
import argparse;

class cmdClient:
	_cmdport = 45000; # Port on which command server should connect.
	_knowncmds = ['READY', 'START', 'STOP', 'STATUS', 'QUIT']; # Unused for now.

	def __init__ (self):
		self._cmd = 'READY';
		self._cmdargs = '';
		self._fid = socket.socket (socket.AF_INET, socket.SOCK_STREAM);
		print '--> Binding on port ', self._cmdport;
		self._fid.bind( ('', self._cmdport) );
		self._runcmd = ['date']; # Default command for the baseclass.

	def run (self):
		print 'In run'
		while (self._cmd.strip() != 'QUIT'): 
			self._fid.listen(1); # Blocking wait
			self._servsock, self._servaddr = self._fid.accept();
			print '--> Received connection from: ', self._servaddr;
			thread.start_new_thread (self.threadhdlr,());

	def threadhdlr (self):
		# NOTE: Had to strip whitespaces, for some reason received commands have 
		# a couple of extra whitespaces at the end. 
		self._recvline = str(self._servsock.recv (1024)).strip().split(' ');
		print 'Received: ', self._recvline, 'len:', len(self._recvline);

		self._cmdproto = self._recvline[0];
		if (self._cmdproto != '0'):
			self._status = 'NOK';
			return;
			
		self._cmd = self._recvline[1];
		self._cmdargs = (' ').join (self._recvline[2:]);
		print 'cmd: ', self._cmd, 'cmdargs: ', self._cmdargs;
		self._status = 'OK';
		if self._cmd is 'START':
			try:
				cmdout = subprocess.check_call (self._runcmd, self._cmdargs, shell=True);
			except CalledProcessError:
				print 'Error in executing process!';
				self._status = 'NOK';

			self._status = self.checkRunStatus(cmdout);


		elif self._cmd is 'STOP':
			# TODO.
#			try:
#				cmdout = subprocess.check_call (self._runcmd, shell=True);
#			except CalledProcessError:
#				print 'Error in executing process!';
			self._status = 'OK';

		self._servsock.send(self._status);

	# Method to show the history of commands received by this cmdclient
	# TODO
	def showcmdhist (self):
		return False;

	def __del__(self):
		# Send termination signal to all threads
		# TODO.
		self._fid.close();	
	
# Processing block specific Cmdclient. Should override the checkRunStatus ()
# method to implement block specific stdout parsing. TODO.

# Object to handle the startup of a pelican server, including generating a 
# status on whether startup was successful, based on parsing the stdout.
class pelicanServerCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = ['start_server.py.in'];
		self._runcmd = ['date'];

	def checkRunStatus (self, output):
		return 'OK';

class pipelineCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = ['start_pipeline.py.in'];
		self._runcmd = ['date'];

	def checkRunStatus (self, output):
		return 'OK';

class gpuCorrCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		self._runcmd = ['date'];

	def checkRunStatus (self, output):
		return 'OK';

class lcuafaacCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		self._runcmd = ['ls -l'];

	def checkRunStatus (self, output):
		return 'OK';


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

