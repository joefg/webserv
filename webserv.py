import os
import sys
import argparse
import logging

import socket
import asyncio

def setup(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.setblocking(False)
    sock.listen(1)
    logging.info(f"Server created at {host}:{port}")

    return sock

def exit(sock):
    sock.close()
    logging.info(f"Server closed.")

def interpret_request(request):
    # What a HTTP request looks like.
    # > GET /index.html HTTP/1.1
    # > Host: localhost:8080
    # > User-Agent: curl/7.80.0
    # > Accept: */*

    req = request.split("\n")

    # Get request type
    req_type = req[0].split("/")[0][:-1]
    req_type = get_http_verb(req_type)

    if req_type is None:
        raise Exception("Invalid request type")

    # Get URL
    url = get_url(req[0])

    # Get filetype
    filetype = get_filetype(url)

    return {
        'req_type' : req_type,
        'url'      : url,
        'filetype' : filetype
    }

def get_filetype(url):
    filetypes = {'html', 'json'}
    ftype = url.split(".")[-1]
    return ftype if ftype in filetypes else 'text'

def get_http_verb(req_type):
    verbs = {'get', 'post', 'put', 'delete', 'patch'}
    return req_type.upper() if req_type.lower() in verbs else None

def get_url(header):
    # begins with /, ends with HTTP
    return header[header.index(' /') + len(' /'):header.index('HTTP') - 1]

def get_response(code):
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

def get_content_type(content_type):
    content_types = {
        'json' : 'Content-Type: application/json;',
        'text' : 'Content-Type: text/plain;',
        'html' : 'Content-Type: text/html;',
    }
    return content_types[content_type]

def make_header(response_code, content_type):
    # What we should make in return.
    # < HTTP/1.1 200 OK
    # < Content-Type: text/html;
    return "\n".join([
        "HTTP/1.1 " + get_response(response_code),
         get_content_type(content_type),
        "\n"
    ])

def open_file(url):
    # On security:
    # This oneliner should remove attempts at using ../../../ to serve files outside of scope.
    path = os.path.relpath(os.path.normpath(os.path.join("/", url)), "/")

    # For security reasons, we also don't serve up hidden files.
    if path[0] == '.' and len(path) > 1:
        raise Exception(f"Hidden files are not served by default. {path}")

    if path == '.':
        path = 'index.html'

    f = open(path, 'r')
    contents = f.read()

    return contents

async def read_request(client):
    request = ''
    while True:
        chunk = (await loop.sock_recv(client, 1024)).decode('utf-8')
        request += chunk
        if len(chunk) < 1024:
            break
    return request

async def handle(client):
    request = await read_request(client)
    req = interpret_request(request)

    try:
        response = make_header('ok', 'html')
        response += open_file(req['url'])
    except:
        logging.exception("Error")
        response = make_header('internal-error', 'text')
        response += "Internal error\n"

    await loop.sock_sendall(client, response.encode('utf-8'))
    client.close()

async def server(sock):
    while True:
        client, addr = await loop.sock_accept(sock)
        loop.create_task(handle(client))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Async web server'
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

    if args['verbose']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    sock = setup(args['host'], args['port'])

    loop = asyncio.get_event_loop() 

    try:
        loop.run_until_complete(server(sock))
    except:
        exit(sock)
