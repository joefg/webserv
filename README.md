# webserv

*The Gang Builds A Web Server*

## Sources

* [Let's Build A Web Server, Ruslan Spivak](https://ruslanspivak.com/lsbaws-part1/);
* [RFC-2616, Hypertext Transfer Protocol -- HTTP/1.1](https://www.w3.org/Protocols/rfc2616/rfc2616.html);
* [Reading 21: Sockets & Networking, MIT 6.005](https://web.mit.edu/6.005/www/fa15/classes/21-sockets-networking/)

## Goals

1. Build a simple web server that listens to a socket and gives a response.
2. Add a method to parse the HTTP request, so that you can return a page if it exists, or error out
	 if it does not exist.
3. Performance enhancements.

## Usage

`python3 webserv.py`

Don't actually use this! Use Apache, Nginx, or Lighttpd instead.
