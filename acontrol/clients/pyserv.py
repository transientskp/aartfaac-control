#!/usr/bin/python

import sys;
import socket;

if __name__ == '__main__':
	print '--> Operating on TCP socket.';
        fid = socket.socket (socket.AF_INET, socket.SOCK_STREAM);
	status = 'OK';
	port = 43000;
        fid.bind( ('', port) );
        print '--> Binding on port ', port;
        fid.listen(1); # Blocking wait
        print '--> Found remote sender';

	clientconn,clientaddr = fid.accept ();

		# Start a thread
        print '--> Conn', clientconn, ' Addr: ', clientaddr;
	line = clientconn.recv (1024);

	print 'Client sent:' ,line;
	print 'We send:', status;
	clientconn.send(status)

	fid.close();
