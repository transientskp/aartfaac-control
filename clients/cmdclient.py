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
# pep/29Jan15
# - Cleared NOK/OK return issues. Multiple transactions now possible on a single TCP session.
# - STOPing a process possible.
# - QUITing cmdclient over TCP possible.
# - Added a ncmdcalls parameter, in case a cmdclient running on a single host needs to run the same command multiple times.
# - Added a genrepeat() function which generates the commandline for a repeat execution.
# - The repeat parameter also allows running different commands on the same host.

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
		self._ncmdcalls = 1; # This instance does not repeat the execution of the desired command.
		self._cmdargs = '';
		print '--> Registering signal handler.';
		signal.signal (signal.SIGINT, self.sighdlr);
		signal.signal (signal.SIGTERM, self.sighdlr);
		self._fid = socket.socket (socket.AF_INET, socket.SOCK_STREAM);
		self._fid.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
		print '--> Binding on port ', self._cmdport;
		self._fid.bind( ('', self._cmdport) );
		self._runcmd = ['date']; # Default command for the baseclass.
		self._proc = [None];
		self._threadid = [-1];   # Will be used to store threadid of command to be run.
		self._env = os.environ.copy();

	def run (self):
		self._fid.listen(1); # Blocking wait
		while (self._cmd.strip() != 'QUIT'): 
			readable, writable, inerror = select.select ([self._fid], [], [], 1);
			for s in readable:
				if s is self._fid:
					self._servsock, self._servaddr = self._fid.accept();
					print '--> Received connection from: ', self._servaddr;
					thread.start_new_thread (self.threadhdlr,());

	def genrepeatcmd (self, repid):
		splitstr = self._recvline.split(' ');
		self._cmdargs = splitstr[2:len(splitstr)];
		return;
		# raise NotImplementedError ("Subclass must implement abstract method.");

	# Signal handler for clean exit on SIGINT and SIGTERM
	def sighdlr (self, signal, frame):
		print '## Signal received! Clean quitting.';
		self._cmd = 'QUIT'
			

	# Thread to service incoming commands.
	def threadhdlr (self):

		while (self._cmd.strip() != 'QUIT'):
			# NOTE: Had to strip whitespaces, for some reason received commands have 
			# a couple of extra whitespaces at the end. 
			self._recvline = str(self._servsock.recv (1024)).strip();
			print 'Received: ', self._recvline, 'len:', len(self._recvline);
	
			self._status = 'NOK';
			splitstr = self._recvline.split(' ');
			self._cmdproto = splitstr[0];
			if (self._cmdproto != '0'):
				print '### Invalid command protocol! Try again.';
				self._servsock.send(self._status);
				continue;
				
			self._cmd = splitstr[1].strip();
			print 'cmd: ', self._cmd;

			if self._cmd == 'START':
				self._cmdargs = splitstr[2:len(splitstr)];
				# Repeat the command if required, asking genrepeatcmd() 
				# to generate the appropriate command
				for ind in range (0, self._ncmdcalls):
					self.genrepeatcmd (ind);
					self._cmdargs[0:0] = self._runcmd;
					# self._cmdargs.insert(0, self._runcmd);
					print '<-- Running cmdstr:',  self._cmdargs;
					try:
						self._proc[ind] = subprocess.Popen (self._cmdargs, env=self._env);
						# We only store the id of the thread which starts a command.
						self._threadid[ind] = thread.get_ident(); 
						
					except subprocess.CalledProcessError:
						print 'Error in executing process!';
						self._status = 'NOK';
					print '<-- Created process with pid %d, threadid %d.' %(self._proc[ind].pid, self._threadid[ind]);
	
				# self._status = self.checkRunStatus(cmdout);
				self._status = 'OK';
				print 'Successfully started process for cmd execution, status:', self._status;
				
	
			elif self._cmd == 'STARTPIPE':
				print 'Running cmdstr:', [self._runcmd, self._cmdargs];
				self._cmdargs = self._recvline.split('|')[0].strip().split(' ');
				self._pipecmd = self._recvline.split('|')[1].strip().split(' ');
				for ind in range (0, self._ncmdcalls):
					self.genrepeatcmd(ind);
					self._cmdargs[0:0] = self._runcmd;
					# self._cmdargs.insert(0, self._runcmd);
					print 'Running cmdstr:',  self._cmdargs;
					try:
						self._proc[ind] = subprocess.Popen (self._cmdargs, env=self._env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
						self._pipe[ind] = subprocess.Popen (self._pipecmd, stdin=self._proc[ind].stdout);
						# We only store the id of the thread which starts a command.
						self._threadid[ind] = thread.get_ident(); 
					except subprocess.CalledProcessError:
						print 'Error in executing process!';
						self._status = 'NOK';

				self._status = 'OK';
				print 'Successfully ran cmd, status:', self._status;
				
			elif self._cmd == 'STOP':
				for ind in range (0, self._ncmdcalls):
					if (self._threadid[ind] > 0):
						print 'Killing pid ', self._proc[ind].pid;
						os.kill (self._proc[ind].pid, signal.SIGTERM);
					
				self._status = 'OK';

			elif self._cmd == 'QUIT':
				self._status = 'OK';

			else:
				print '### Cmd %s not understood. Try again.' % self._cmd;
				self._status = 'NOK';
	
			self._servsock.send(self._status);


	# Method to show the history of commands received by this cmdclient
	# TODO
	def showcmdhist (self):
		return False;

	def __del__(self):
		# Send termination signal to all threads
		# TODO.
		if (hasattr(self, '_fid')):
			print '<-- Closing socket.';
			self._fid.close();	
	
# Processing block specific Cmdclient. Should override the checkRunStatus ()
# method to implement block specific stdout parsing. TODO.

# Object to handle the startup of a pelican server, including generating a 
# status on whether startup was successful, based on parsing the stdout.
class pelicanServerCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		self._runcmd = ['start_server.py'];
		# self._runcmd = 'watch -n1 date';

	def checkRunStatus (self, output):
		return 'OK';


# Multiple pipelines need to be started based on the number of processors 
# available on the client machine.
# We reimplement the  genrepeatcmd() function for this.
class pipelineCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		self._runcmd = ['start_pipeline.py'];
		self._ncmdcalls = 4;
		# self._runcmd = 'watch -n1 date ';

	def checkRunStatus (self, output):
		return 'OK';

	# Generate a new monitor port for each instantiation.
	# We assume the command arguments are of the form:
	# 192.168.1.1 4200 /data/output
	def genrepeatcmd (self, repid):
		index = self._recvline.find('--monitor-port');
		monport=int(self._recvline[index:].split(' ')[1]);
		recvline_copy = self._recvline.replace(str(monport), str(monport+repid)); # Make changes to the copy
		splitstr = recvline_copy.split(' ');
		self._cmdargs = splitstr[2:len(splitstr)];
		return;
	
class gpuCorrCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		# self._runcmd = 'watch -n1 date';
		# self._runcmd = '/home/pprasad/gpu-corr/afaac_GPU_interface/src/run.rt.nodel.dop312';
		self._env["DISPLAY"]=":0";
		self._env["PLATFORM"]="AMD Accelerated Parallel Processing";
		self._env["TYPE"] = "GPU"
		# self._runcmd = 'numactl -C 11-19 /home/romein/projects/Triple-A/AARTFAAC/installed/AARTFAAC ';
		self._runcmd = ['/home/pprasad/gpu-corr/Triple-A/AARTFAAC/AARTFAAC'];

	def checkRunStatus (self, output):
		return 'OK';


class lcuafaacCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		self._runcmd = ['watch -n1 date'];

	def checkRunStatus (self, output):
		return 'OK';

	def genrepeatcmd (self, repid):
		splitstr = self._recvline.split(' ');
		self._cmdargs = splitstr[2:len(splitstr)];
		return;

class rtmonCmdClient (cmdClient):
	def __init__ (self):
		cmdClient.__init__(self);
		self._runcmd = ['atv.py'];
		# self._runcmd = ['python', '/usr/local/lib/python2.7/dist-packages/rtmon/atv.py'];

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
		cl = pelicanServerCmdClient();

	elif client.procblk.lower() == 'rtmon':
		cl = rtmonCmdClient ();

	else:
		print '### Unknown processing block!';
		sys.exit (-1);

	cl.run();	
	del (cl);

