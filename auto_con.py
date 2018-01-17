#!/usr/bin/python
import socket
import sys

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening


if len(sys.argv) < 3:
	print "Usage: <sync [click|export [today|yesterday]] |clonecheck clonecheck|assign assign|kba|sfrule> <cmd>"
	sys.exit(-11)

server_address = "/run/lock/%s" % sys.argv[1]
print >>sys.stderr, 'connecting to %s %s' % (sys.argv[1], server_address)
try:
	sock.connect(server_address)
except socket.error, msg:
	print >>sys.stderr, msg
	sys.exit(1)

try:
	# Send data
	args = sys.argv[2:]
	message = ' '.join(args);
	print >>sys.stderr, 'sending "%s"' % message
	sock.sendall(message)

	amount_received = 0
	amount_expected = len(message)
	data = sock.recv(256)
	amount_received += len(data)
	print >>sys.stderr, 'received "%s"' % data

finally:
	sock.close()
