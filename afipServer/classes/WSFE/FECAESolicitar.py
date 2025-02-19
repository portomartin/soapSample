from errors_utils import Error, Observation, errors_serialize, InvalidRequest

import random
import datetime

from FECAESolicitarTypes import *

# --------------
# FECAESolicitar
# --------------
class FECAESolicitar:
	
	def __init__(self):
		None

	# run
	def run(self, FeCAEReq):

		print("------")
		print(FeCAEReq)
		print("------")
		
		observations = validate_receipt(FeCAEReq)
		print("observations", observations)
		
		ret = authorize_receipt()
		print("ret", ret)

		ret = FECAEResponse()		
		return ret
		
db = {}
if 'tokens' not in db:
	db['tokens'] = {}

if 'last_auth_doc' not in db:
	db['last_auth_doc'] = {}

if 'CAE' not in db:
	db['CAE'] = {}

if 'CAEA' not in db:
	db['CAEA'] = {}

if 'CAEA_data' not in db:
	db['CAEA_data'] = {}

if 'receipts' not in db:
	db['receipts'] = {}

if 'CAEA_unused' not in db:
	db['CAEA_unused'] = {}

if 'CAEA_used' not in db:
	db['CAEA_used'] = {}		
		
def get_datetime():
	"""Returns the server's datetime."""

	return datetime.datetime.today()
	
def increment_last_auth_doc():
	"""Increments by 1 the number of the last authorized document."""

	pos, doc_type = 1, 1
	if pos not in db['last_auth_doc']:
		db['last_auth_doc'][pos] = {}

	current = get_last_auth_doc()
	db['last_auth_doc'][pos][doc_type] = current + 1	

def get_last_auth_doc():
        """Returns the number of the last authorized document for the given document type. If no
        document was authorized yet, returns 0."""

        pos, doc_type = 1, 1
        return db['last_auth_doc'].get(pos, {}).get(doc_type, 0)		
		
def generate_cae():
        """Generates a CAE for the given document number."""

        pos, doc_type, doc_num = 1, 1, 1
        # if get_last_auth_doc() + 1 != doc_num:
            # raise InvalidReceiptNumber()

        if pos not in db['CAE']:
            db['CAE'][pos] = {}

        if doc_type not in db['CAE'][pos]:
            db['CAE'][pos][doc_type] = {}

        db['CAE'][pos][doc_type][doc_num] = random.randint(0, 99999999999999)

        return db['CAE'][pos][doc_type][doc_num]		

def authorize_receipt():
	"""Authorizes the given receipt. `receipt` is the parsed XML representation received in the
	request for the `FECAEDetRequest` element, and `xml_namespace` is the name space used in the
	request. Also, `doc_type` is a code indicating the document type.
	You can raise `InvalidRequest` exceptions to simulate errors."""

	pos, doc_type, doc_num = 1, 1, 1

	# if receipt is not None:
		# self.validate_receipt(receipt=receipt, xml_namespace=xml_namespace, doc_type=doc_type)

	# generates the CAE if the document number is correct
	cae = generate_cae()

	cae_due_date = get_datetime() + datetime.timedelta(days=10)

	if pos not in db['receipts']:
		db['receipts'][pos] = {}

	if doc_type not in db['receipts'][pos]:
		db['receipts'][pos][doc_type] = {}

	db['receipts'][pos][doc_type][doc_num] = {
		'authorization_code': cae,
		'due_date': cae_due_date,
		'process_datetime': get_datetime(),
		'authorization_type': 'CAE',
	}

	increment_last_auth_doc()

	return db['receipts'][pos][doc_type][doc_num]

def validate_receipt(FeCAEReq):
	"""Called when a receipt is received for authorization. `receipt` is the parsed XML
	representation received in the request for the `FECAEDetRequest` element, and `xml_namespace`
	is the name space used in the request. Also, `doc_type` is a code indicating the document type.
	You can raise `InvalidRequest` exceptions to simulate errors."""

	from decimal import Decimal

	vat_rates = {
		'3': Decimal('0.00'),
		'4': Decimal('10.50'),
		'5': Decimal('21.00'),
		'6': Decimal('27.00'),
		'8': Decimal('5.00'),
		'9': Decimal('2.50'),
	}
	
	print("FeCAEReq", FeCAEReq)
	print("FeCAEReq.FeDetReq.FECAEDetRequest.ImpTotal", FeCAEReq.FeDetReq.FECAEDetRequest.ImpTotal)

	CATEGORY_C_DOC_CODES = ['11', '13']

	total = FeCAEReq.FeDetReq.FECAEDetRequest.ImpTotal
	other_taxes = FeCAEReq.FeDetReq.FECAEDetRequest.ImpTrib
	taxable_net_amount = FeCAEReq.FeDetReq.FECAEDetRequest.ImpNeto
	exempt_net_amount = FeCAEReq.FeDetReq.FECAEDetRequest.ImpOpEx
	non_taxable_net_amount = FeCAEReq.FeDetReq.FECAEDetRequest.ImpTotConc
	tax_total = FeCAEReq.FeDetReq.FECAEDetRequest.ImpIVA
	vat_list = FeCAEReq.FeDetReq.FECAEDetRequest.Iva

	doc_type = '11'
	observations = []
	
	# CATEGORY_C
	if doc_type in CATEGORY_C_DOC_CODES:	
		
		if non_taxable_net_amount != Decimal('0.00'):
			observations.append(Observation(code='10043', msg='El campo ImpTotConc (Importe Total del Concepto) para comprobantes tipo C debe ser igual a cero (0).'))
			
		if exempt_net_amount != Decimal('0.00'):
			observations.append(Observation(code='10044', msg='El campo ImpOpEx (importe exento) para comprobantes tipo C debe ser igual a cero (0).'))
			
		if tax_total != Decimal('0.00'):
			observations.append(Observation(code='10047', msg='El campo ImpIVA (Importe de IVA) para comprobantes tipo C debe ser igual a cero (0).'))
			
		if taxable_net_amount + other_taxes != total:
			observations.append(Observation(code='10048', msg="El campo  'Importe Total' ImpTotal, debe ser igual  a la  suma de ImpNeto + ImpTrib. Donde ImpNeto es igual al Sub Total"))
			
		if vat_list is not None:
			observations.append(Observation(code='10071', msg='Para comprobantes tipo C el objeto IVA no debe informarse.'))

		if len(observations) > 0:
			return observations
	
	# NOT CATEGORY_C
	if doc_type not in CATEGORY_C_DOC_CODES:
	
		tax_base = Decimal('0.00')
		tax_total_from_vats = Decimal('0.00')

		if vat_list is not None:
			for vat in vat_list:
		
				vat_id = vat.AlicIva.Id				
				vat_tax_base = Decimal(vat.AlicIva.BaseImp)				
				vat_amount = Decimal(vat.AlicIva.Importe)

				if vat_tax_base == Decimal('0.00'):
					observations=[Observation(code='10020', msg='El  campo  BaseImp  en AlicIVA es obligatorio  y debe ser mayor a 0 cero.')]
					return observations

				expected_vat_amount = Decimal(str(round(vat_tax_base * vat_rates[vat_id] / Decimal('100.00'), 2)))
				vat_amount_error_tolerance = Decimal('0.01')
				if  vat_amount < expected_vat_amount - vat_amount_error_tolerance or vat_amount > expected_vat_amount + vat_amount_error_tolerance:
					observations=[Observation(code='10051', msg='Los importes informados en AlicIVA no se corresponden con los porcentajes.')]
					return observations

				if vat_id != '3' and tax_total == Decimal('0.00'):
					observations=[Observation(code='10018', msg='Si ImpIva es igual a 0 el objeto Iva y AlicIva son obligatorios. Id iva = 3 (iva 0)')]
					return observations

				tax_base += vat_tax_base
				tax_total_from_vats += vat_amount
				
		else:
			if taxable_net_amount > Decimal('0.00'):
				observations=[Observation(code='10070', msg='Si ImpNeto es mayor a 0 el objeto IVA es obligatorio.')]
				return observations
		
	# Check Totals
	observations = []

	total_obtained = non_taxable_net_amount + taxable_net_amount + exempt_net_amount + other_taxes + tax_total

	if total_obtained != total:
		observations.append(Observation(code='10048', msg="El campo  'Importe Total' ImpTotal, debe ser igual  a la  suma de ImpTotConc + ImpNeto + ImpOpEx + ImpTrib + ImpIVA."))

	if tax_total != tax_total_from_vats:
		observations.append(Observation(code='10023', msg='La suma de los campos Importe en IVA debe ser igual al valor ingresado en ImpIVA.'))

	if taxable_net_amount != tax_base:
		observations.append(Observation(code='10061', msg='La suma de los campos BaseImp en AlicIva debe ser igual al valor ingresado en ImpNeto.'))

	if len(observations) > 0:
		return observations
		
