from suds.client import Client

if __name__ == "__main__":	
	url = 'https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl'
	url = 'http://0.0.0.0:5002/wsfev1/service.asmx?wsdl'
	client = Client(url=url, cache=None)  # server doesn't work with cache None
	print client
	# d = client.service.FEDummy()