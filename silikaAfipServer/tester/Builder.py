from collections import namedtuple
from datetime import datetime, timedelta

VatAmount = namedtuple('VatAmount', 'type, net_amount, amount')

class Builder:

	# __init__
	def __init__(self):
		print ("init")

	# ----------
	# build_vats
	# ----------
	def build_vats(self, vats):
		"""Returns the XML defining the array of VATs in the receipt.
		`vats` must be an iterable where each element is of type `VatAmount` that contains the
		VAT type, tax base (base imponible) and vat amount."""

		def serialize_vat(vat):
			return '<ar:AlicIva>' \
						'<ar:Id>%(type)d</ar:Id>' \
						'<ar:BaseImp>%(net_amount)s</ar:BaseImp>' \
						'<ar:Importe>%(amount)s</ar:Importe>' \
					'</ar:AlicIva>' % vat._asdict()

		return '<ar:Iva>%s</ar:Iva>' % '\n'.join(map(serialize_vat, vats))


	# ------------------
	# build_receipt_data
	# ------------------
	def build_receipt_data(self, doc_num, doc_type, cuit=None, pos=None, assoc_doc_num=None, assoc_doc_date=None):
		"""Returns the XML defining the receipt data."""

		receipt_a_codes = [1, 3]
		receipt_c_codes = [11, 13]
		credit_note_codes = {
		  3: 1,
		  8: 6,
		  13: 11,
		}

		concept = 1 # products
		doc_date = datetime.now().strftime('%Y%m%d')
		currency_id, currency_price = 'PES', '1.000000'
		# id_type, id_num = 96, 35317279  # type of buyer's tributary ID and the ID itself
		id_type, id_num = 99, 0  # type of buyer's tributary ID and the ID itself

		if doc_type in receipt_c_codes:
		
		  gross_total, untaxed_net_total, net_total, untaxed_total = '90.50', '0.00', '90.50', '0.00'
		  vat_total, tributes_total = '0.00', '0.00'
		  vats = ''  # type -> FEParamGetTiposIva
		  
		else:
		
		  if doc_type in receipt_a_codes:
			id_type, id_num = 80, 30584620389  # type of buyer's tributary ID and the ID itself

		  gross_total, untaxed_net_total, net_total, untaxed_total = '104.00', '1.00', '90.50', '3.00'
		  vat_total, tributes_total = '9.51', '0.00'
		  vats = self.build_vats([VatAmount(type=4, net_amount='90.50', amount='9.51')])  # type -> FEParamGetTiposIva

		associated_docs = ''
		
		if doc_type in credit_note_codes.keys():
		
		  assoc_doc_type = credit_note_codes[doc_type]
		  associated_docs = """
			<ar:CbtesAsoc>
			  <ar:CbteAsoc>
				<ar:Tipo>%(assoc_doc_type)d</ar:Tipo>
				<ar:PtoVta>%(pos)d</ar:PtoVta>
				<ar:Nro>%(doc_num)d</ar:Nro>
				<ar:Cuit>%(cuit)s</ar:Cuit>
				<ar:CbteFch>%(assoc_doc_date)s</ar:CbteFch>
			  </ar:CbteAsoc>
			</ar:CbtesAsoc>
			  """ % locals()

		return """
			<ar:Concepto>%(concept)d</ar:Concepto>
			<ar:DocTipo>%(id_type)d</ar:DocTipo>
			<ar:DocNro>%(id_num)d</ar:DocNro>
			<ar:CbteDesde>%(doc_num)d</ar:CbteDesde>
			<ar:CbteHasta>%(doc_num)d</ar:CbteHasta>
			<ar:CbteFch>%(doc_date)s</ar:CbteFch>
			<ar:ImpTotal>%(gross_total)s</ar:ImpTotal>
			<ar:ImpTotConc>%(untaxed_net_total)s</ar:ImpTotConc>
			<ar:ImpNeto>%(net_total)s</ar:ImpNeto>
			<ar:ImpOpEx>%(untaxed_total)s</ar:ImpOpEx>
			<ar:ImpTrib>%(tributes_total)s</ar:ImpTrib>
			<ar:ImpIVA>%(vat_total)s</ar:ImpIVA>
			<ar:MonId>%(currency_id)s</ar:MonId>
			<ar:MonCotiz>%(currency_price)s</ar:MonCotiz>
			%(vats)s
			%(associated_docs)s""" % locals()


	# -----------------
	# build_auth_header
	# -----------------		
	def build_auth_header(self, token):
		"""Returns the XML defining the authentication header.
		`token` must be a valid Token instance obtained from the WSAA."""

		return """
		<ar:Auth>
			<ar:Token>%(token)s</ar:Token>
			<ar:Sign>%(sign)s</ar:Sign>
			<ar:Cuit>%(id)s</ar:Cuit>
		</ar:Auth>""" % token._asdict()

		
	# -----------------
	# build_cae_request
	# -----------------
	def build_cae_request(self, token, pos, doc_type, doc_num, assoc_doc_num=None, assoc_doc_date=None):
		"""Returns the XML payload for the CAE request.
		`token` must be a valid Token instance obtained from the WSAA.
		`doc_num` is the number of the document to authorize.
		`assoc_doc_num` is the number of the associated document (in case of debit or credit notes).
		`assoc_doc_date` is the date of the associated document.
		"""

		auth = self.build_auth_header(token)
		num_records = 1
		receipt_data = self.build_receipt_data(doc_num=doc_num, doc_type=doc_type, cuit=token._asdict()['id'], pos=pos, assoc_doc_num=assoc_doc_num, assoc_doc_date=assoc_doc_date)

		return """<?xml version="1.0"?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
		  <soapenv:Header/>
		  <soapenv:Body>
			<ar:FECAESolicitar>
			  %(auth)s
			  <ar:FeCAEReq>
				<ar:FeCabReq>
				  <ar:CantReg>%(num_records)d</ar:CantReg>
				  <ar:PtoVta>%(pos)d</ar:PtoVta>
				  <ar:CbteTipo>%(doc_type)d</ar:CbteTipo>
				</ar:FeCabReq>
				<ar:FeDetReq>
				  <ar:FECAEDetRequest>
					%(receipt_data)s
				  </ar:FECAEDetRequest>
				</ar:FeDetReq>
			  </ar:FeCAEReq>
			</ar:FECAESolicitar>
		  </soapenv:Body>
		</soapenv:Envelope>
		""" % locals()

		
	# -----------------
	# build_auth_header
	# -----------------
	def build_auth_header(self, token):
		"""Returns the XML defining the authentication header.
		`token` must be a valid Token instance obtained from the WSAA."""

		return """
		<ar:Auth>
			<ar:Token>%(token)s</ar:Token>
			<ar:Sign>%(sign)s</ar:Sign>
			<ar:Cuit>%(id)s</ar:Cuit>
		</ar:Auth>""" % token._asdict()
		
	
	# ------------------
	# build_caea_request
	# ------------------
	def build_caea_request(self, token, period, fortnight):
		"""Returns the XML payload for the CAEA request.
		`token` must be a valid Token instance obtained from the WSAA."""

		auth = build_auth_header(token)

		return """<?xml version="1.0"?>
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
		  <soapenv:Header/>
		  <soapenv:Body>
			<ar:FECAEASolicitar>
			  %(auth)s
			  <ar:Periodo>%(period)s</ar:Periodo>
			  <ar:Orden>%(fortnight)d</ar:Orden>
			</ar:FECAEASolicitar>
		  </soapenv:Body>
		</soapenv:Envelope>
		""" % locals()
		"""Sends a request to the WSFE to obtain a CAEA for the given period. Returns the authorized CAEA.
		`token` must be a Token instance with the fields obtained from the WSAA (not expired)."""

	