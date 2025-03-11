import logging

from flask import Flask, jsonify, request
from spyne import Application, rpc, Iterable, Integer, Unicode
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
from spyne.util.wsgi_wrapper import WsgiMounter

# owner
from WSFE import *
from WSAA import *
 
# WebServer
class WebServer:
	
	def __init__(self):
	
		self.host = "0.0.0.0"
		self.port = 5001
		self.server = ''
		self.database = ''
 
	# run
	def run(self):
	
		logging.basicConfig(level=logging.DEBUG)
		logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

		WSFE.event_manager.add_listener('method_return_string', on_method_return_string)
		
		wsaa = Application([WSAA], 'http://wsaa.view.sua.dvadac.desein.afip.gov', in_protocol=Soap11(validator='lxml'), out_protocol=Soap11())
		wsfe = Application([WSFE], 'http://ar.gov.afip.dif.FEV1/', in_protocol=Soap11(validator='lxml'), out_protocol=Soap11())

		wsgi_wsfe = WsgiMounter({
			'service.asmx': wsfe
		})

		wsgi_wsaa = WsgiMounter({
			'LoginCms': wsaa,
		})

		wsgi_root = WsgiMounter({
			"wsfev1": wsfe,
			'ws': wsaa
		})

		server = make_server(self.host, self.port, wsgi_root)
		print("Server Started")
		print("WSFE is at: http://{0}:{1}{2}".format(self.host, self.port, "/wsfev1/service.asmx?WSDL"))
		print("WSAA is at: http://{0}:{1}{2}".format(self.host, self.port, '/ws/services/LoginCms?WSDL'))
		server.serve_forever()
		
		
		
		# from werkzeug.wsgi import DispatcherMiddleware
		# from apps import spyned
		# from apps.flasked import app

		# # SOAP services are distinct wsgi applications, we should use dispatcher
		# # middleware to bring all aps together
		# app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
			# '/soap': WsgiApplication(spyned.create_app(app))
		# })


		# if __name__ == '__main__':
			# app.run()
		
		
		

def on_method_return_string(ctx):
	print("using listener")
	ctx.out_string[0] = ctx.out_string[0].replace("tns:", "")