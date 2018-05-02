#!/usr/bin/env python

import socket
import sys
import os
import numpy as np

server_address = './uds_socket'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the address
print('starting up on {}'.format(server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(4096)
            print('received {!r}'.format(data))
            if data:
                print('sending frame back to the client')

                msg = np.zeros(2000*(3+3+1))
                for i in range(0, 2000):
                    msg[i*7:(i+1)*7] = np.append(50*np.random.rand(3)-25, np.array([0,0,1.0,10.0]))


                connection.sendall(msg.nbytes.to_bytes(4, byteorder=sys.byteorder))

                print('sending message of length {}'.format(len(msg)))
                connection.sendall(msg)
            else:
                print('no data from', client_address)
                break

            

    finally:
        # Clean up the connection
        connection.close()

