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

            response = self.make_header('ok', 'text')
            response += "HELLO WORLD!"

            client_conn.sendall(response.encode())
            logging.info(f"Sent: {response}")
            client_conn.close()

    def make_header(self, response_code, content_type):
        return "\n".join([
            "HTTP/1.1 " + self.get_response(response_code),
            self.get_content_type(content_type),
            "\n"
        ])

    def get_response(self, code):
        responses = {
            'continue':                       '100 Continue',
            'switching-protocols':            '101 Switching Protocols',
            'processing':                     '102 Processing',
            'ok':                             '200 OK',
            'created':                        '201 Created',
            'accepted':                       '202 Accepted',
            'non-authoritative':              '203 Non-Authoritative Information',
            'no-content':                     '204 No Content',
            'reset-content':                  '205 Reset Content',
            'partial-content':                '206 Partial Content',
            'multi-status':                   '207 Multi-Status',
            'already-reported':               '205 Already Reported',
            'im-used':                        '205 IM Used',
            'multiple-choices':               '300 Multiple Choices',
            'permanent':                      '301 Moved Permanently',
            'found':                          '302 Found',
            'see-other':                      '303 See Other',
            'not_modified':                   '304 Not Modified',
            'use-proxy':                      '305 Use Proxy',
            'temporary-redirect':             '307 Temporary Redirect',
            'permanant-redirect':             '308 Permanent Redirect',
            'bad-request':                    '400 Bad Request',
            'unauthorised':                   '401 Unauthorized',
            'payment':                        '402 Payment Required',
            'forbidden':                      '403 Forbidden',
            'not-found':                      '404 Not Found',
            'method-not-allowed':             '405 Method Not Allowed',
            'not-acceptable':                 '406 Not Acceptable',
            'proxy-auth-needed':              '407 Proxy Authentication Required',
            'timeout':                        '408 Request Timeout',
            'conflict':                       '409 Conflict',
            'gone':                           '410 Gone',
            'length-required':                '411 Length Required',
            'precondition-failed':            '412 Precondition Failed',
            'payload-too-large':              '413 Payload Too Large',
            'request-uri-too-long':           '414 Request-URI Too Long',
            'unsupported-media-type':         '415 Unsupported Media Type',
            'range-not-satisfiable':          '416 Requested Range Not Satisfiable',
            'expectation-failed':             '417 Expectation Failed',
            'teapot':                         '418 I\'m a teapot',
            'misdirected':                    '421 Misdirected Request',
            'unprocessable':                  '422 Unprocessable Entity',
            'locked':                         '423 Locked',
            'failed-dependency':              '424 Failed Dependency',
            'upgrade-required':               '426 Upgrade Required',
            'precondition-required':          '428 Precondition Required',
            'too-many-requests':              '429 Too Many Requests',
            'fields-too-large':               '431 Request Header Fields Too Large',
            'connection-closed':              '444 Connection Closed Without Response',
            'censorship':                     '451 Unavailable For Legal Reasons',
            'client-closed':                  '499 Client Closed Request',
            'internal-error':                 '500 Internal Server Error',
            'not-implemented':                '501 Not Implemented',
            'bad-gateway':                    '502 Bad Gateway',
            'service-unavailable':            '503 Service Unavailable',
            'gateway-timeout':                '504 Gateway Timeout',
            'unsupported':                    '505 HTTP Version Not Supported',
            'variant-negotiates':             '506 Variant Also Negotiates',
            'storage':                        '507 Insufficient Storage',
            'loop':                           '508 Loop Detected',
            'not-extended':                   '510 Not Extended',
            'network-authorisation-required': '511 Network Authentication Required',
            'network-timeout':                '599 Network Connect Timeout Error'
        }
        return responses[code]

    def get_content_type(self, content_type):
        content_types = {
            'json' : 'Content-Type: application/json;',
            'text' : 'Content-Type: text/plain;',
            'html' : 'Content-Type: text/html;',
        }
        return content_types[content_type]

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
