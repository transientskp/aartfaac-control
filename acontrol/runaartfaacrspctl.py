#!/usr/bin/python
# Script to allow setting of subbands for AARTFAAC by acontrol.
# Created to allow acontrol to execute only the rspctl command 
# on the station LCUs.
# Peeyush Prasad, 10Jul15


try:
	import subprocess;
	import re;
except ImportError:
	print 'Module subprocess or re not found. Quitting.'

try:
	import optparse;
	import time;
except ImportError:
	print 'Module optparse not found. Quitting.'
import sys;

try:
	import numpy as np;
except ImportError:
	print 'Module Numpy not found. Quitting.'

def main():
	runcmd = ['rspctl', '--sdo'];
	parser = optparse.OptionParser("Usage: %prog --subbands subband1,subband2,subband3,...");
	parser.add_option ("-s", "--subbands", dest="subbands", type="string", help="Specify the subbands to be selected as a csv list. Limited to 36 (constraint set by hardware).", default='276, 277, 278, 279, 280, 281, 282, 283');

	(options, arg) = parser.parse_args();
	try:
		subbands = np.array ([int (strsubband) for strsubband in options.subbands.split(',')]);
	except:
		print '### Unable to split provided subband list. Quitting.'
		sys.exit (-1);

	if (len(subbands) > 36):
		print '<-- Unable to set more than 36 subbands for AARTFAAC. Taking the first 36.'
		subbands = subbands[0:35];

	# Set the unspecified subbands to 0
	subbands = np.append (subbands, np.zeros (36-len(subbands)))

	# Check if subbands lie between 0 and 511
	if (np.any(subbands > 511) or np.any (subbands < 0)):
		print '### Invalid subband supplied.';
		sys.exit (-1);

	# Carry out the rspctl command,  collect its stdout/stderr
	tmp = '=';
	for sb in subbands:
		tmp += "%.0f,"%sb;
	runcmd[1] += tmp[:-1];
	try:
		print '<-- Running command: ', runcmd;
		p1 = subprocess.Popen (runcmd, stdout=subprocess.PIPE);
		cmdoutput, err = p1.communicate();
	except CalledProcessError:
		print '### Command not found!'
		sys.exit (-1);

	# Check if the command was executed successfully
	"""Expected output:
	bits per sample=16
	rcumask.count()=96
	3; 144
	setsdoack.timestamp=0 - Thu, 01 Jan 1970 00:00:00.000000  +0000
	"""
	print 'Cmd output is :', cmdoutput[0:512];

	# Query the set subbands. For the default subbands, output is like:
	"""
	RCU[93].subbands=1 x 36
[       553       555       557       559       561       563       565 
        567         1         1         1         1         1         1 
          1         1         1         1         1         1         1 
          1         1         1         1         1         1         1 
          1         1         1         1         1         1         1 
          1 ]

RCU[94].subbands=1 x 36
[       552       554       556       558       560       562       564 
        566         0         0         0         0         0         0 
          0         0         0         0         0         0         0 
          0         0         0         0         0         0         0 
          0         0         0         0         0         0         0 
          0 ]

RCU[95].subbands=1 x 36
[       553       555       557       559       561       563       565 
        567         1         1         1         1         1         1 
          1         1         1         1         1         1         1 
          1         1         1         1         1         1         1 
          1         1         1         1         1         1         1 
          1 ]
	"""
	# NOTE: This sleep is important to make sure that the correct values 
	# of the set subbands are read.
	time.sleep(5);	
	runcmd[1] = '--sdo';

	# Move to subprocess.check_output () if python is upgraded to >2.7. 
	p2 = subprocess.Popen (runcmd, stdout=subprocess.PIPE);
	cmdoutput2, err2 = p2.communicate();

	# Only checking whether the first polarization's subbands are set.
	st_ind  = re.search ('RCU\[ 0\]\.subbands=1 x 36\\n\[', cmdoutput2).end();
	end_ind = re.search (']\\n\\nRCU\[ 1\]\.subbands=1 x 36', cmdoutput2).start();
	set_subbands = [int(sb) for sb in cmdoutput2[st_ind:end_ind].replace ('\\n', ' ').split()];

	expected_subbands = subbands*2;
	if (np.all(expected_subbands == set_subbands)):
		print '<-- AARTFAAC subbands successfully set.'
		return 0;
	else:
		print '### ERROR in setting AARTFAAC subbands.'
		print '### Set     : ', set_subbands;
		print '### Expected:', expected_subbands;
		return -1;


if __name__ == '__main__':
	main();
