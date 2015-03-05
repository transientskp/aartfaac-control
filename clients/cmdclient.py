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
import select;
import os;
import signal;

class cmdClient:
	_cmdport = 45000; # Port on which command server should connect.
	_knowncmds = ['READY', 'START', 'STOP', 'STATUS', 'QUIT']; # Unused for now.

	def __init__ (self):
		self._cmd = 'READY';
		self._cmdargs = '';
		self._fid = socket.socket (socket.AF_INET, socket.SOCK_STREAM);
		self._fid.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
		print '--> Binding on port ', self._cmdport;
		self._fid.bind( ('', self._cmdport) );
		self._runcmd = 'date'; # Default command for the baseclass.
		self._threadid = -1;   # Will be used to store threadid of command to be run.

	def run (self):
		self._fid.listen(1); # Blocking wait
		while (self._cmd.strip() != 'QUIT'): 
			readable, writable, inerror = select.select ([self._fid], [], [], 1);
			for s in readable:
				if s is self._fid:
					self._servsock, self._servaddr = self._fid.accept();
					print '--> Received connection from: ', self._servaddr;
					thread.start_new_thread (self.threadhdlr,());

	# Thread to service incoming commands.
	def threadhdlr (self):

		while (self._cmd.strip() != 'QUIT'):
			# NOTE: Had to strip whitespaces, for some reason received commands have 
			# a couple of extra whitespaces at the end. 
			self._recvline = str(self._servsock.recv (1024)).strip().split(' ');
			print 'Received: ', self._recvline, 'len:', len(self._recvline);
	
			self._cmdproto = self._recvline[0];
			if (self._cmdproto != '0'):
				self._status = 'NOK';
				return;
				
			self._cmd = self._recvline[1].strip();
			self._cmdargs = (' ').join (self._recvline[2:]);
			print 'cmd: ', self._cmd, 'cmdargs: ', self._cmdargs;
			self._status = 'NOK';

			if self._cmd == 'START':
				print 'Running cmdstr:', [self._runcmd, self._cmdargs];
				try:
					self._proc = subprocess.Popen ([self._runcmd, self._cmdargs], shell=True);
					# We only store the id of the thread which starts a command.
					self._threadid = thread.get_ident(); 
				except subprocess.CalledProcessError:
					print 'Error in executing process!';
					self._status = 'NOK';
	
				# self._status = self.checkRunStatus(cmdout);
				print 'Successfully ran cmd, status:', self._status;
				
	
			elif self._cmd == 'STOP':
				if (self._threadid > 0):
					print 'Killing pid ', self._proc.pid;
					os.kill (self._proc.pid, signal.SIGTERM);
					
				self._status = 'OK';

			elif self._cmd == 'QUIT':
				self._status = 'OK';

			else:
				self._status = 'NOK';
	
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
		self._runcmd = 'watch -n1 date';

	def checkRunStatus (self, output):
		return 'OK';

class pipelineCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = ['start_pipeline.py.in'];
		self._runcmd = 'watch -n1 date ';

	def checkRunStatus (self, output):
		return 'OK';

class gpuCorrCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = 'watch -n1 date ';
		self._runcmd = '/home/pprasad/gpu-corr/afaac_GPU_interface/src/run.rt.nodel.dop312';

	def checkRunStatus (self, output):
		return 'OK';

class lcuafaacCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		self._runcmd = 'watch -n1 date';

	def checkRunStatus (self, output):
		return 'OK';


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--procblk", help="Specify which processing block this cmdclient controls. Options: gpucorr = GPU correlator\n lcuafaac = AARTFAAC LCU ,pelicanpipeline = Pelican pipeline, pelicanserver = Pelican Server.", default='gpucorr');
	client = parser.parse_args();

	if client.procblk.lower() == 'gpucorr':
		cl = gpuCorrCmdClient ();

	elif client.procblk.lower() == 'lcuafaac':
		cl = lcuafaacCmdClient();	

	elif client.procblk.lower() == 'pelicanpipeline':
		cl = pipelineCmdClient();

	elif client.procblk.lower() == 'pelicanserver':
		cl = pelicanserverCmdClient();

	else:
		print '### Unknown processing block!';
		sys.exit (-1);

	cl.run();	

