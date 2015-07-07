#!/usr/bin/python
# Script to allow setting of subbands for AARTFAAC by acontrol.
# Created to allow acontrol to execute only the rspctl command 
# on the station LCUs.


try:
	import subprocess;
except ImportError:
	print 'Module subprocess not found. Quitting.'

try:
	import argparse;
except ImportError:
	print 'Module argparse not found. Quitting.'
import sys;

try:
	import numpy as np;
except ImportError:
	print 'Module Numpy not found. Quitting.'

def main():
	runcmd = ['rspctl'];
	parser = argparse.ArgumentParser()
	parser.add_argument("--subbands", help="Specify the subbands to be selected as a csv list. Limited to 36 (constraint set by hardware).", default='276, 277, 278, 279, 280, 281, 282, 283');

	client = parser.parse_args();
	try:
		subbands = np.array ([int (strsubband) for strsubband in client.subbands.split(',')]);
	except:
		print 'Unable to split provided subband list. Quitting.'
		sys.exit (-1);

	# Check if subbands lie between 0 and 511
	if (np.any(subbands > 511) or np.any (subbands < 0)):
		print '### Invalid subband supplied.';
		sys.exit (-1);

	# Carry out the rspctl command,  collect its stdout/stderr
	runcmd.append ('--sdo=%s'%str(subbands));
	try:
		print '<-- Running command: ', runcmd;
		cmdoutput = subprocess.check_output (runcmd, stderr=subprocess.STDOUT, shell=True);
	except CalledProcessError:
		print '### Command not found!'
		sys.exit (-1);

	# Check if the command was executed successfully
	print 'Cmd output is :', cmdoutput;
	if cmdoutput

	# Return a status to the caller.
	return 0;
	

if __name__ == '__main__':
	main();
