import socket
import threading
import time
import sys
import os
import struct

"""
Change the HOST and PORT if needed. 
Other constant vars are ok to keep default value.
"""
# Empty is local default.
HOST =''
PORT = 60061

BUFFER_SIZE = 1024
# Define bytes format of file head info, 128si means 128 bytes string + integer.
FILE_HEAD_FORMAT = '128si'

# Reply a file back to client.
def _send_file(filepath, conn):
	if os.path.isfile(filepath):
            fileinfo_size = struct.calcsize(FILE_HEAD_FORMAT)
            # Define file head, including filename and file size.
            fhead = struct.pack(FILE_HEAD_FORMAT, os.path.basename(filepath).encode(),os.stat(filepath).st_size)
            conn.sendall(fhead)
            print('client filepath: {0}'.format(filepath))

            fp = open(filepath, 'rb')
            while 1:
                data = fp.read(BUFFER_SIZE)
                if not data:
                    print('{0} file send over...'.format(filepath))
                    break
                conn.send(data)

# Receive data and process it.
def _process_data(conn, addr):
    print('Accept new connection from {0}'.format(addr))
    # conn.settimeout(500)
    conn.sendall(b'Hi, Welcome to the server!')

    while 1:
        fileinfo_size = struct.calcsize(FILE_HEAD_FORMAT)
        buf = conn.recv(fileinfo_size)
        print('buf: ', buf, 'fileinfo-size: ', fileinfo_size)
        if buf:
            filename, filesize = struct.unpack(FILE_HEAD_FORMAT, buf)
            fn = filename.strip(b'\00').decode()
            new_filename = os.path.join('./', 'new_' + fn)
            print('file new name is {0}, filesize is {1}'.format(new_filename, filesize))
            print('start receiving...')
            fp = open(new_filename, 'wb')
            recvd_size = 0
            while recvd_size < filesize:
                read_size = min(BUFFER_SIZE, filesize - recvd_size)
                data = conn.recv(read_size)
                fp.write(data)
                recvd_size += len(data)
            fp.close()
            print('end receive...')
            print('start reply...')
            _send_file(new_filename, conn)
        conn.close()
        break

def _socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:
        conn, addr = s.accept()
        t = threading.Thread(target=_process_data, args=(conn, addr))
        t.start()

if __name__ == '__main__':
    _socket_service()