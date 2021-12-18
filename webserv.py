import os
import sys
import argparse
import logging

import socket

class Webserv(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        logging.info(f"Server created at {self.host}:{self.port}")

    def serve(self):
        while True:
            client_conn, client_addr = self.socket.accept()
            request = client_conn.recv(1024)
            logging.info(request.decode('utf-8'))

            response = "HTTP/1.1 200 OK\n\nHELLO WORLD"

            client_conn.sendall(response.encode())
            logging.info(f"Sent: {response}")
            client_conn.close()

    def __str__(self):
        return f"Webserv host={self.host} port={self.port}"

    def __repr__(self):
        return "Webserv"

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.socket.close()
        logging.info("Socket terminated.")
        return self

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Terminal Application'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Increase output verbosity'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8080
    )
    parser.add_argument(
        '--host',
        type=str,
        default='localhost'
    )
    args = vars(parser.parse_args())
    logging.basicConfig(level=logging.INFO)

    with Webserv(args['host'], args['port']) as w:
        print(w)
        w.serve()
