from zeep import Client
from lxml import etree
from datetime import datetime
from datetime import timedelta
import uuid
import itertools
from subprocess import call
import re
from Logger import *

# LoginCms
class LoginCms:

	# __init__
	def __init__(self):
		self.client = None	
		self.token = None
		self.sign = None
		self.cuit = None
		self.logger = Logger()
		
	# buildRequest
	def buildRequest(self):
		
		root = etree.Element('loginTicketRequest')
		root.set("version", "1.0")

		header = etree.Element('header')
		uniqueId = etree.Element('uniqueId')
		uniqueId.text = str(uuid.uuid4().int & (1<<64)-1)
		uniqueId.text = "290926"
		header.append(uniqueId)
		
		generationTime = etree.Element('generationTime')
		g = datetime.today() - timedelta(minutes=60)
		generationTime.text = g.strftime('%Y-%m-%dT%H:%M:%S-03:00')
		header.append(generationTime)
		
		expirationTime = etree.Element('expirationTime')
		e = datetime.today() + timedelta(minutes=60)
		expirationTime.text = e.strftime('%Y-%m-%dT%H:%M:%S-03:00')
		header.append(expirationTime)
		
		root.append(header)
		
		service = etree.Element('service')
		service.text = 'wsfe'
		root.append(service)
		
		s = etree.tostring(root, pretty_print=False)
		# print(s)
		
		f = open('curl/MiLoginTicketRequest.xml', 'wb' )
		f.write(s)
		f.close()
		
	# buildRequestCms
	def buildRequestCms(self):
	
		self.logger.info('Generating MiLoginTicketRequest.xml.cms')
		
		dir = "curl/"
		cmd = f"openssl cms -sign -in {dir}MiLoginTicketRequest.xml -out {dir}MiLoginTicketRequest.xml.cms -signer {dir}MiCertificado.pem -inkey {dir}MiClavePrivada.key -nodetach -outform PEM"
		# print(cmd)
		decrypted = call(cmd, shell=True)
		
	# extractParam
	def extractParam(self):
	
		dir = "curl/"
		file = f"{dir}MiLoginTicketRequest.xml.cms"
		
		f = open(file)
		lines = f.read()
		f.close()
		
		lines = lines.replace("-----BEGIN CMS-----", "")
		lines = lines.replace("-----END CMS-----", "")
		return lines
		
	# readTA
	def readTA(self):
	
		dir = ""
		file = f"{dir}TA.xml"		
		doc = etree.parse(file)
		
		result = doc.find("*/token") 
		self.token = result.text
		
		result = doc.find("*/sign") 
		self.sign = result.text
		
		result = doc.find("*/destination") 
		res = re.findall(r'\d+', result.text)
		self.cuit = res[0]

	# getNewToken
	def getNewToken(self):

		self.buildRequest()
		self.buildRequestCms()
		in0 = self.extractParam()
		self.logger.info('Running loginCms')
		print(self.client.service.loginCms(in0))

	# getToken
	def getToken(self):	
		self.logger.info('Reading current token')	
		self.readTA()




