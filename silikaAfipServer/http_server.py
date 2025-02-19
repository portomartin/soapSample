import re
import ssl
import sys
import json
import tempfile
import http.server
import logging

from threading import Thread
from collections import namedtuple, defaultdict
from future.utils import iteritems

try:
	import urllib.parse as urlparse
except ImportError:
	import urlparse



class Dispatcher(object):
	_handlers = {}

	def __init__(self, handlers):
		self._handlers = {re.compile(self._url_patt_to_regex(
			k)): v for k, v in iteritems(handlers)}

	def _url_patt_to_regex(self, url_patt):
		return r'^' + re.sub(r'{:(\w+)}', r'(?P<\1>\\w+)', url_patt) + r'$'

	def dispatch(self, handler):
	
	
		url_parts = urlparse.urlparse(handler.path)
		query_params = urlparse.parse_qs(
			url_parts.query, strict_parsing=True) if url_parts.query else {}

		print ("dispatch", url_parts, query_params)
		
		for url, h in iteritems(self._handlers):
		
			match = re.search(url, url_parts.path)
			
			if match:
				path_params = match.groupdict()
				print ("dispatch", handler, query_params, path_params)
				return h(handler, query_params, path_params)
				
		else:
			return False


class Handler(http.server.BaseHTTPRequestHandler):

	def __init__(self, GET_handlers, POST_handlers, *args, **kw):
	
		self.post_dispatcher = Dispatcher(POST_handlers)
		self.get_dispatcher = Dispatcher(GET_handlers)

		http.server.BaseHTTPRequestHandler.__init__(self, *args, **kw)

	def _handle(self, dispatcher):
	
		print ("_handle")
	
		self.body_contents = None
		if 'Content-Length' in self.headers:
			self.body_contents = self.rfile.read(int(self.headers['Content-Length']))

		if dispatcher.dispatch(self):
			return True
			
		else:
			self.send_response(404)
			self.end_headers()
			return False

	def send_error(self, status_code, error, message):
		self.send_response(status_code)
		self.end_headers()
		self.wfile.write(
			'{{"error":"{error}","message":"{message}","status":{status_code}}}'.format(**locals()).encode('utf-8'))

	def body(self):
		return self.body_contents

	def json(self):
		return json.loads(self.body_contents)

	# def log_request(self, *args):
		# """Stops access logging."""
		# pass

	def do_GET(self):
		# logging.basicConfig(level=logging.INFO)
		# logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
		return self._handle(self.get_dispatcher)		

	def do_POST(self):
		print("do_POST")
		return self._handle(self.post_dispatcher)

	def do_PUT(self):
		return self._handle(self.put_dispatcher)

	def do_DELETE(self):
		return self._handle(self.delete_dispatcher)


class Server(http.server.HTTPServer):

	def __init__(self, host, port, GET_handlers, POST_handlers, ca_cert=None, certfile=None):
		def handler_factory(*args, **kw):
			"""This function allows the indirection so that `Handler` instances have the dispatchers
			dynamically registered to the server."""

			return Handler(GET_handlers, POST_handlers, *args, **kw)

		http.server.HTTPServer.__init__(self, (host, port), handler_factory)
		self._started = False

		if ca_cert is not None:
			with tempfile.NamedTemporaryFile(delete=False) as f:
				certfile = f.name
				f.write(ca_cert.encode('utf-8'))

		protocol = 'http'
		if certfile is not None:
			self.socket = ssl.wrap_socket(self.socket, certfile=certfile, server_side=True)
			protocol = 'https'

		self.url = '%s://%s:%d' % (protocol, host, port)

	def start(self):
		self._thread = Thread(target=self.serve_forever)
		self._thread.start()
		self._started = True

	def stop(self):
		self.shutdown()
		if self._started:
			self.server_close()
			self._thread.join()


# if __name__ == '__main__':

	# def status_handler(handler, query_params, path_params):
		# handler.send_response(200)
		# handler.end_headers()
		# handler.wfile.write('ok!\n')
		# return True

	# def post_test_handler(handler, query_params, path_params):
		# handler.send_response(200)
		# handler.end_headers()
		# handler.wfile.write('POST /post -> %s\n' % path_params)
		# return True

	# GET_handlers = {
		# '/status': status_handler,
	# }
	# POST_handlers = {
		# '/post/{:test}': post_test_handler,
	# }

	# server = Server('localhost', 9999, GET_handlers, POST_handlers)
	# server.start()
