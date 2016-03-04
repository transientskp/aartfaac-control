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
import datetime;

class cmdClient(object):
	_cmdport = 45000; # Port on which command server should connect.
	# knowncmds Unused for now.
	_knowncmds = ['READY', 'START', 'STOP', 'STATUS', 'QUIT']; 

	def __init__ (self, cmdport):
		self._cmd = 'READY';
		self._cmdport = cmdport;
		# Allow repetition of execution of the desired command.
		self._ncmdcalls = 1; 
		self._cmdargs = '';
		print '--> [%s]   Registering signal handler.' \
		% datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");

		signal.signal (signal.SIGINT, self.sighdlr);
		signal.signal (signal.SIGTERM, self.sighdlr);
		self._fid = socket.socket (socket.AF_INET, socket.SOCK_STREAM);
		self._fid.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
		print '--> [%s]   Binding on port %d.' \
		% (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \

		self._cmdport);
		self._fid.bind( ('', self._cmdport) );
		self._runcmd = ['date']; # Default command for the baseclass.
		self._proc = [];
		self._pipe = [];

		# Will be used to store threadid of command to be run.
		self._threadid = [];   
		self._env = os.environ.copy();

	def run (self):
		self._fid.listen(1); # Blocking wait

		while (self._cmd.strip() != 'QUIT'): 
			readable, writable, inerror = \
				select.select ([self._fid], [], [], 1);

			for s in readable:

				if s is self._fid:
					self._servsock, self._servaddr = self._fid.accept();
					print '--> [%s]    Received connection from: %s.' \
					%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),\
					self._servaddr);

					thread.start_new_thread (self.threadhdlr,());

	def genrepeatcmd (self, repid):
		splitstr = self._recvline.split(' ');
		self._cmdargs = splitstr[2:len(splitstr)];
		return;
		# raise NotImplementedError("Subclass must implement abstract method.");

	# Signal handler for clean exit on SIGINT and SIGTERM
	def sighdlr (self, signal, frame):
		print '### [%s]   Signal received! Clean quitting.', \
			datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");
		self._cmd = 'STOP'
			

	# Thread to service incoming commands.
	def threadhdlr (self):

		while (self._cmd.strip() != 'QUIT'):
			# NOTE: Had to strip whitespaces, for some reason received commands
			# have a couple of extra whitespaces at the end. 
			self._recvline = str(self._servsock.recv (1024)).strip();
			print '--> [%s]   Received: %s, len: %d.' \
			% (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
			self._recvline, len(self._recvline));

			# Looks like the remote side closed the connection!
			if (len (self._recvline) == 0): 
				print '### Remote side closed connection: Aborting.\n';
				self._status = 'OK';
				break;
	
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
				self._cmdargs[0:0] = self._runcmd;
				# Repeat the command if required, asking genrepeatcmd() 
				# to generate the appropriate command

				for ind in range (0, self._ncmdcalls):
					# self.genrepeatcmd (ind);
					# self._cmdargs.insert(0, self._runcmd);
					print '<-- [%s]   Running cmdstr: %s.' \
					% (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
					 self._cmdargs);

					try:
						self._proc.append(subprocess.Popen (self._cmdargs, \
						env=self._env, preexec_fn=os.setsid));
						# only store the id of the thread which starts a cmd.
						self._threadid.append(thread.get_ident()); 
						self._status = 'OK';
						print \
						'<-- [%s]   Successfully started pid %d for cmd execution, status: %s.' \
						%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),\
						self._proc[ind].pid, self._status);

						# self._proc[ind].wait();
						
					except (subprocess.CalledProcessError,OSError) as err:
						print '### [%s]   Error in executing process! [%s]' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), repr(err));
						if (self._status == 'OK'):
							continue
						self._status = 'NOK';
						# self._servsock.send(self._status);
	
				# self._status = self.checkRunStatus(cmdout);
				self._servsock.send(self._status);
				
	
			elif self._cmd == 'STARTPIPE':
				self._cmdargs = self._recvline.split('|')[0].strip().split(' ');
				self._pipecmd = self._recvline.split('|')[1].strip().split(' ');

				for ind in range (0, self._ncmdcalls):
					# self.genrepeatcmd(ind); # No monitor port functionality in pipelines now.
					self._cmdargs[0:0] = self._runcmd;
					# self._cmdargs.insert(0, self._runcmd);
					print '<-- [%s]   Running cmdstr: %s.' \
					% (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
					self._cmdargs);

					try:
						self._proc.append(subprocess.Popen \
						(self._cmdargs, env=self._env, stdout=subprocess.PIPE, \
						stderr=subprocess.STDOUT, preexec_fn=os.setsid));

						self._pipe.append(subprocess.Popen (self._pipecmd, \
						stdin=self._proc[ind].stdout, preexec_fn=os.setsid));
						# only store the id of the thread which starts a cmd.
						self._threadid.append(thread.get_ident()); 
						self._status = 'OK';
						print '<-- [%s]   Successfully started pid %d for cmd execution, status: %s.' \
						%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),\
						self._proc[ind].pid, self._status);

						self._servsock.send(self._status);
						# self._proc[ind].wait();
					except subprocess.CalledProcessError:
						print '### [%s]   Error in executing process!' \
						% datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");
						self._status = 'NOK';
						self._servsock.send(self._status);

				
			elif self._cmd == 'STOP':

				for proc in self._proc:

					if (proc.poll() == None): # Child  has not terminated
						print '<-- [%s]   Terminating pid %d.' \
						%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),\
						proc.pid);
						os.killpg (proc.pid, signal.SIGTERM);
						proc.wait(); # Prevent zombie processes
						# proc.kill();

				for ind in range (0, len(self._proc)):
					self._proc.pop();
					
				self._status = 'OK';
				self._servsock.send(self._status);

			elif self._cmd == 'QUIT':
				print '<-- [%s]   Quitting cmdClient.' \
				% (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"));
				self._status = 'OK';
				self._servsock.send(self._status);

			else:
				print '### [%s]   Cmd %s not understood. Try again.' \
				% (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),\
			 	self._cmd);
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
			print '<-- [%s]   Closing socket' \
			% (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"));
			self._fid.close();	
	
# Processing block specific Cmdclient. Should override the checkRunStatus ()
# method to implement block specific stdout parsing. TODO.

# Object to handle the startup of a pelican server, including generating a 
# status on whether startup was successful, based on parsing the stdout.
class pelicanServerCmdClient (cmdClient):
	def __init__ (self, cmdport):
		cmdClient.__init__(self, cmdport);
		self._runcmd = ['start_server.py'];
		self._ncmdcalls = 1;
		# self._runcmd = 'watch -n1 date';

	def checkRunStatus (self, output):
		return 'OK';


# Multiple pipelines need to be started based on the number of processors 
# available on the client machine.
# We reimplement the  genrepeatcmd() function for this.
class pipelineCmdClient (cmdClient):
	def __init__ (self, cmdport):
		cmdClient.__init__(self, cmdport);
		self._runcmd = ['start_pipeline.py'];
		# Determine the number of CPUs available 

		try:
			import multiprocessing;
			# python 2.6, number of virtual CPUs.
			self._ncmdcalls = multiprocessing.cpu_count();
		except (NotImplementedError, ImportError):
			print '### Could not determine number of cpus, defaulting to 4';
			self._ncmdcalls = 4;


	def checkRunStatus (self, output):
		return 'OK';

	# Generate a new monitor port for each instantiation.
	# We assume the command arguments are of the form:
	# 192.168.1.1 4200 /data/output
	def genrepeatcmd (self, repid):
		index = self._recvline.find('--monitor-port');
		monport=int(self._recvline[index:].split(' ')[1]);

		# Make changes to the copy
		recvline_copy = self._recvline.replace(str(monport),str(monport+repid));
		splitstr = recvline_copy.split(' ');
		self._cmdargs = splitstr[2:len(splitstr)];
		return;
	
class gpuCorrCmdClient (cmdClient):
	def __init__ (self, cmdport):
		cmdClient.__init__(self, cmdport);
		self._ncmdcalls = 1;
		self._env["DISPLAY"]=":0";
		self._env['GPU_FORCE_64BIT_PTR'] ="1";
		self._env["PLATFORM"]="AMD Accelerated Parallel Processing";
		self._env["TYPE"] = "GPU"
		# self._runcmd = 'numactl -C 11-19 /home/romein/projects/Triple-A/AARTFAAC/installed/AARTFAAC ';
		self._runcmd = ['numactl', '-i',  '0-1', '/home/romein/projects/Triple-A/AARTFAAC/installed/AARTFAAC'];

	def checkRunStatus (self, output):
		return 'OK';


class lcuafaacCmdClient (cmdClient):
	def __init__ (self, cmdport):
		cmdClient.__init__(self, cmdport);
		self._runcmd = ['watch -n1 date'];

	def checkRunStatus (self, output):
		return 'OK';

	def genrepeatcmd (self, repid):
		splitstr = self._recvline.split(' ');
		self._cmdargs = splitstr[2:len(splitstr)];
		return;

class rtmonCmdClient (cmdClient):
	def __init__ (self, cmdport):
		cmdClient.__init__(self, cmdport);
		self._runcmd = ['atv.py'];
		# self._runcmd = ['python', '/usr/local/lib/python2.7/dist-packages/rtmon/atv.py'];

	def checkRunStatus (self, output):
		return 'OK';

class catCmdClient (cmdClient):
	def __init__ (self, cmdport):
		cmdClient.__init__(self, cmdport);
		self._runcmd = ['cat'];

	def checkRunStatus (self, output):
		return 'OK';

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--procblk", \
		help="Specify which processing block this cmdclient controls.\n \
		Options: gpucorr         = GPU correlator\n \
				 lcuafaac        = AARTFAAC LCU\n \
				 pelicanpipeline = Pelican pipeline\n \
				 pelicanserver   = Pelican Server\n \
				 cat             = cat a file\n.", default='gpucorr');
	parser.add_argument ("--cmdport", \
				help="Specify the port on which cmdclient should wait for \
					 commands. Default 45000", default=45000);

	client = parser.parse_args();

	if client.procblk.lower() == 'gpucorr':
		cl = gpuCorrCmdClient (int(client.cmdport));

	elif client.procblk.lower() == 'lcuafaac':
		cl = lcuafaacCmdClient(int(client.cmdport));	

	elif client.procblk.lower() == 'pelicanpipeline':
		cl = pipelineCmdClient(int(client.cmdport));

	elif client.procblk.lower() == 'pelicanserver':
		cl = pelicanServerCmdClient(int(client.cmdport));

	elif client.procblk.lower() == 'rtmon':
		cl = rtmonCmdClient (int(client.cmdport));

	elif client.procblk.lower() == 'cat':
		cl = catCmdClient (int(client.cmdport));

	else:
		print '### Unknown processing block!';
		sys.exit (-1);

	cl.run();	
	del (cl);

