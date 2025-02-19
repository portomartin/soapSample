from collections import namedtuple
import requests
from datetime import datetime, timedelta

from Builder import Builder
from Token import Token

WSAA_URL, WSFEv1_URL = "http://0.0.0.0:9999", "http://0.0.0.0:10000"
VatAmount = namedtuple('VatAmount', 'type, net_amount, amount')

class Tester:

	# __init__
	def __init__(self):
		self.builder = Builder()
		self.token = Token()
		print ("init")

	# build
	def build(self):
		print ("build")
		
		
	def FECAESolicitar(self):
		"""Sends a request to the WSFE to obtain the CAE for a particular document. Returns the CAE and
		authorization date.
		`token` must be a Token instance with the fields obtained from the WSAA (not expired)."""
	
		req = self.builder.build_cae_request(token=self.token.token, pos=1, doc_type=6, doc_num=1)

		# executes the SOAP method
		response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
								 data=req,
								 headers={
									'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAESolicitar',
									'Content-Type': 'text/xml',
								})

		if not response.ok:
			code, message = parse_fault(response.text)
			raise SOAPFault(code, message)

		return response.text
		
	# request_caea
	def FECAEASolicitar(self):	
		
		# CAE related methods
		# 
		# Requests a CAE
		# request_cae(token=token, pos=<POS number>, doc_type=<Factura A, B, etc>, doc_num=<Document number>, assoc_doc_num=<Associated document number>, assoc_doc_date=<Assoc. doc. date>)
		# examples:
		# print request_caea(token=token, pos=1, doc_type=6, doc_num=1)

		req = self.builder.build_caea_request(token=token.token, period='202108', fortnight=2)
		print (req)
		# print request_caea(token=token, period='202108', fortnight=2)
		# token=token, pos=1, doc_type=6, doc_num=1

		# executes the SOAP method
		response = requests.post('%s/wsfev1/service.asmx' % WSFEv1_URL,
								 data=req,
								 headers={
									'SOAPAction': 'http://ar.gov.afip.dif.FEV1/FECAEASolicitar',
									'Content-Type': 'text/xml',
								})

		if not response.ok:
			code, message = parse_fault(response.text)
			raise SOAPFault(code, message)

		return response.text
