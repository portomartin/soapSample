import elba
import random
import cert_utils
import datetime
import calendar
import time

from WSAA import parse_token
from http_server import Server
from handlers.wsfev1 import FECAEASolicitar, FECAESolicitar, FECAEAConsultar, FECAEARegInformativo, FECAEASinMovimientoInformar, FECompUltimoAutorizado, FECompConsultar, FEDummy
from handlers.wsfev1 import soap_error_action_missing, InvalidReceiptNumber, Error, Observation, InvalidRequest


def _WSFEv1_handler(handler, query_params, path_params):
    """Handles SOAP requests to the WSFv1 service."""

    actions = {
        'http://ar.gov.afip.dif.FEV1/FECAEASolicitar': FECAEASolicitar,
        'http://ar.gov.afip.dif.FEV1/FECAEAConsultar': FECAEAConsultar,
        'http://ar.gov.afip.dif.FEV1/FECAEARegInformativo': FECAEARegInformativo,
        'http://ar.gov.afip.dif.FEV1/FECAEASinMovimientoInformar': FECAEASinMovimientoInformar,
        'http://ar.gov.afip.dif.FEV1/FECAESolicitar': FECAESolicitar,
        'http://ar.gov.afip.dif.FEV1/FECompUltimoAutorizado': FECompUltimoAutorizado,
        'http://ar.gov.afip.dif.FEV1/FECompConsultar': FECompConsultar,
        'http://ar.gov.afip.dif.FEV1/FEDummy': FEDummy,
        None: soap_error_action_missing,
    }
    soap_action = handler.headers.get('SOAPAction')

    actions[soap_action](handler)
    return True


def get_caea_dates(current_datetime, period, fortnight):
    """Calculates the dates from and until which the CAEA will be valid, the deadline date to inform
    the receipts authorized with it, and its process date."""

    period_datetime = datetime.datetime.strptime(period, '%Y%m')
    if fortnight == '1':
        first_request_datetime = period_datetime - datetime.timedelta(days=5)
        last_request_datetime = period_datetime + datetime.timedelta(days=14, hours=23, minutes=59, seconds=59)

        valid_from = period_datetime
    elif fortnight == '2':
        first_request_datetime = period_datetime + datetime.timedelta(days=10)
        last_request_datetime = period_datetime + datetime.timedelta(days=calendar.monthrange(period_datetime.year, period_datetime.month)[1] - 1,
                                                                     hours=23,
                                                                     minutes=59,
                                                                     seconds=59)

        valid_from = period_datetime + datetime.timedelta(days=15)
    else:
        raise InvalidRequest(errors=[Error(code='15005',
                                           msg='Campo  Orden: Debe ser igual a 1 o 2.')])

    if current_datetime < first_request_datetime or current_datetime > last_request_datetime:
        first_request_date = first_request_datetime.strftime('%d/%m/%Y')
        last_request_date = last_request_datetime.strftime('%d/%m/%Y')
        raise InvalidRequest(errors=[Error(code='15006',
                                           msg='Fecha de envio podra ser desde 5 dias corridos anteriores al inicio hasta el ' + \
                                               'ultimo dia de cada quincena. Del %s hasta %s' % (first_request_date, last_request_date))])

    valid_until = last_request_datetime
    information_deadline = valid_until + datetime.timedelta(days=5)

    return valid_from, valid_until, information_deadline, current_datetime


class WSFEv1(Server):
    """Fake server to simulate some functionality from the WSFEv1. `db` is dict where all the
    state of the server is stored. This state must be shared with with the WSAA service in order
    to work correctly."""

    def __init__(self, host, port, db):
        POST_handlers = {'/wsfev1/service.asmx': _WSFEv1_handler}
        GET_handlers = {}

        # maps valid tokens to the corresponding tributary IDs (CUIT)
        self.db = db
        if 'tokens' not in db:
            self.db['tokens'] = {}

        if 'last_auth_doc' not in self.db:
            self.db['last_auth_doc'] = {}

        if 'CAE' not in self.db:
            self.db['CAE'] = {}

        if 'CAEA' not in self.db:
            self.db['CAEA'] = {}

        if 'CAEA_data' not in self.db:
            self.db['CAEA_data'] = {}

        if 'receipts' not in self.db:
            self.db['receipts'] = {}

        if 'CAEA_unused' not in self.db:
            self.db['CAEA_unused'] = {}

        if 'CAEA_used' not in self.db:
            self.db['CAEA_used'] = {}

        # calls the parent constructor with the handlers to simulate the WSAA
        Server.__init__(self, host, port, GET_handlers, POST_handlers)

    def get_datetime(self):
        """Returns the server's datetime."""

        return datetime.datetime.today()

    def validate_receipt(self, receipt, xml_namespace, doc_type):
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

        CATEGORY_C_DOC_CODES = ['11', '13']

        total = Decimal(receipt.find('ar:ImpTotal', xml_namespace).text)
        other_taxes = Decimal(receipt.find('ar:ImpTrib', xml_namespace).text)

        taxable_net_amount = Decimal(receipt.find('ar:ImpNeto', xml_namespace).text)
        exempt_net_amount = Decimal(receipt.find('ar:ImpOpEx', xml_namespace).text)
        non_taxable_net_amount = Decimal(receipt.find('ar:ImpTotConc', xml_namespace).text)
        tax_total = Decimal(receipt.find('ar:ImpIVA', xml_namespace).text)

        vat_list = receipt.find('ar:Iva', xml_namespace)

        if doc_type in CATEGORY_C_DOC_CODES:
            observations = []
            if non_taxable_net_amount != Decimal('0.00'):
                observations.append(Observation(code='10043',
                                                      msg='El campo ImpTotConc (Importe Total del Concepto) para comprobantes tipo C debe ser igual a cero (0).'))
            if exempt_net_amount != Decimal('0.00'):
                observations.append(Observation(code='10044',
                                                      msg='El campo ImpOpEx (importe exento) para comprobantes tipo C debe ser igual a cero (0).'))
            if tax_total != Decimal('0.00'):
                observations.append(Observation(code='10047',
                                                      msg='El campo ImpIVA (Importe de IVA) para comprobantes tipo C debe ser igual a cero (0).'))
            if taxable_net_amount + other_taxes != total:
                observations.append(Observation(code='10048',
                                                      msg="El campo  'Importe Total' ImpTotal, debe ser igual  a la  suma de ImpNeto + ImpTrib. Donde ImpNeto es igual al Sub Total"))
            if vat_list is not None:
                observations.append(Observation(code='10071',
                                                      msg='Para comprobantes tipo C el objeto IVA no debe informarse.'))

            if len(observations) > 0:
                raise InvalidRequest(observations=observations)
        else:
            tax_base = Decimal('0.00')
            tax_total_from_vats = Decimal('0.00')

            if vat_list is not None:
                for vat in vat_list.findall('ar:AlicIva', xml_namespace):
                    vat_id = vat.find('ar:Id', xml_namespace).text
                    vat_tax_base = Decimal(vat.find('ar:BaseImp', xml_namespace).text)
                    vat_amount = Decimal(vat.find('ar:Importe', xml_namespace).text)

                    if vat_tax_base == Decimal('0.00'):
                        raise InvalidRequest(observations=[Observation(code='10020',
                                                                       msg='El  campo  BaseImp  en AlicIVA es obligatorio  y debe ser mayor a 0 cero.')])

                    expected_vat_amount = Decimal(str(round(vat_tax_base * vat_rates[vat_id] / Decimal('100.00'), 2)))
                    vat_amount_error_tolerance = Decimal('0.01')
                    if  vat_amount < expected_vat_amount - vat_amount_error_tolerance or vat_amount > expected_vat_amount + vat_amount_error_tolerance:
                        raise InvalidRequest(observations=[Observation(code='10051',
                                                                       msg='Los importes informados en AlicIVA no se corresponden con los porcentajes.')])

                    if vat_id != '3' and tax_total == Decimal('0.00'):
                        raise InvalidRequest(observations=[Observation(code='10018',
                                                                       msg='Si ImpIva es igual a 0 el objeto Iva y AlicIva son obligatorios. Id iva = 3 (iva 0)')])

                    tax_base += vat_tax_base

                    tax_total_from_vats += vat_amount
            else:
                if taxable_net_amount > Decimal('0.00'):
                    raise InvalidRequest(observations=[Observation(code='10070',
                                                                   msg='Si ImpNeto es mayor a 0 el objeto IVA es obligatorio.')])

            observations = []

            total_obtained = non_taxable_net_amount + taxable_net_amount + exempt_net_amount + other_taxes + tax_total

            if total_obtained != total:
                observations.append(Observation(code='10048',
                                                msg="El campo  'Importe Total' ImpTotal, debe ser igual  a la  " + \
                                                    "suma de ImpTotConc + ImpNeto + ImpOpEx + ImpTrib + ImpIVA."))

            if tax_total != tax_total_from_vats:
                observations.append(Observation(code='10023', msg='La suma de los campos Importe en IVA debe ser igual al valor ingresado en ImpIVA.'))

            if taxable_net_amount != tax_base:
                observations.append(Observation(code='10061', msg='La suma de los campos BaseImp en AlicIva debe ser igual al valor ingresado en ImpNeto.'))

            if len(observations) > 0:
                raise InvalidRequest(observations=observations)

    def generate_cae(self, pos, doc_type, doc_num):
        """Generates a CAE for the given document number."""

        pos, doc_type, doc_num = str(pos), str(doc_type), int(doc_num)
        if self.get_last_auth_doc(pos=pos, doc_type=doc_type) + 1 != doc_num:
            raise InvalidReceiptNumber()

        if pos not in self.db['CAE']:
            self.db['CAE'][pos] = {}

        if doc_type not in self.db['CAE'][pos]:
            self.db['CAE'][pos][doc_type] = {}

        self.db['CAE'][pos][doc_type][doc_num] = random.randint(0, 99999999999999)

        return self.db['CAE'][pos][doc_type][doc_num]

    def get_cae(self, pos, doc_type, doc_num):
        """Returns the generated CAE for a particular receipt."""

        pos, doc_type, doc_num = str(pos), str(doc_type), int(doc_num)
        return self.db['CAE'][pos][doc_type][doc_num]

    def generate_caea(self, period, fortnight):
        """Generates a CAEA for the given period and fortnight."""

        valid_from, valid_until, information_deadline, processed_datetime = get_caea_dates(self.get_datetime(), period, fortnight)

        period, fortnight = str(period), int(fortnight)
        if self.get_caea(period=period, fortnight=fortnight) is not None:
            raise InvalidRequest(errors=[Error(code='15008',
                                               msg='Existe un CAEA otorgado para la CUIT solicitante con el periodo y orden informado. ' + \
                                                   'Consultar el metodo FECAEAConsultar.')])

        if period not in self.db['CAEA']:
            self.db['CAEA'][period] = {}

        caea = random.randint(0, 99999999999999)

        self.db['CAEA'][period][fortnight] = {
            'CAEA': caea,
            'valid_from': valid_from,
            'valid_until': valid_until,
            'information_deadline': information_deadline,
            'processed_datetime': processed_datetime,
        }

        self.db['CAEA_data'][caea] = self.db['CAEA'][period][fortnight]

        return self.db['CAEA'][period][fortnight]

    def get_caea(self, period, fortnight):
        """Returns the generated CAEA for the given period and fortnight."""

        period, fortnight = str(period), int(fortnight)
        return self.db['CAEA'].get(period, {}).get(fortnight, None)

    def retrieve_existent_caea(self, period, fortnight):
        """Returns the CAEA for the given period and fortnight, which must exist."""

        period, fortnight = str(period), int(fortnight)
        
        caea = self.get_caea(period=period, fortnight=fortnight)
        if caea is None:
            raise InvalidRequest(errors=[Error(code='602',
                                               msg='No existen datos en nuestros registros para los parametros ingresados.')])

        return caea

    def authorize_receipt(self, pos, doc_type, doc_num, receipt=None, xml_namespace=None):
        """Authorizes the given receipt. `receipt` is the parsed XML representation received in the
        request for the `FECAEDetRequest` element, and `xml_namespace` is the name space used in the
        request. Also, `doc_type` is a code indicating the document type.
        You can raise `InvalidRequest` exceptions to simulate errors."""

        pos, doc_type, doc_num = str(pos), str(doc_type), int(doc_num)

        if receipt is not None:
            self.validate_receipt(receipt=receipt, xml_namespace=xml_namespace, doc_type=doc_type)

        # generates the CAE if the document number is correct
        cae = self.generate_cae(pos=pos, doc_type=doc_type, doc_num=doc_num)

        cae_due_date = self.get_datetime() + datetime.timedelta(days=10)

        if pos not in self.db['receipts']:
            self.db['receipts'][pos] = {}

        if doc_type not in self.db['receipts'][pos]:
            self.db['receipts'][pos][doc_type] = {}

        self.db['receipts'][pos][doc_type][doc_num] = {
            'authorization_code': cae,
            'due_date': cae_due_date,
            'process_datetime': self.get_datetime(),
            'authorization_type': 'CAE',
        }

        self.increment_last_auth_doc(pos=pos, doc_type=doc_type)

        return self.db['receipts'][pos][doc_type][doc_num]

    def inform_receipt(self, pos, doc_type, doc_num, caea, receipt=None, xml_namespace=None):
        """Informs a receipt authorized using the given CAEA. `receipt` is the parsed XML
        representation received in the request for the `FECAEARegInformativo` element, and
        `xml_namespace` is the name space used in the request. Also, `doc_type` is a code indicating
        the document type.
        You can raise `InvalidRequest` exceptions to simulate errors."""

        pos, doc_type, doc_num, caea = str(pos), str(doc_type), int(doc_num), int(caea)

        if receipt is not None:
            self.validate_receipt(receipt=receipt, xml_namespace=xml_namespace, doc_type=doc_type)

        # checks the receipt number is valid
        if self.get_last_auth_doc(pos=pos, doc_type=doc_type) + 1 != doc_num:
            raise InvalidReceiptNumber()

        # TODO: check CAEA is valid
        due_date = self.db['CAEA_data'][caea]['valid_until']

        if pos not in self.db['receipts']:
            self.db['receipts'][pos] = {}

        if doc_type not in self.db['receipts'][pos]:
            self.db['receipts'][pos][doc_type] = {}

        self.db['receipts'][pos][doc_type][doc_num] = {
            'authorization_code': caea,
            'due_date': due_date,
            'process_datetime': self.get_datetime(),
            'authorization_type': 'CAEA',
        }

        # marks the CAEA as used for the given POS
        if caea not in self.db['CAEA_used']:
            self.db['CAEA_used'][caea] = []

        self.db['CAEA_used'][caea].append(pos)

        self.increment_last_auth_doc(pos=pos, doc_type=doc_type)

        return self.db['receipts'][pos][doc_type][doc_num]

    def inform_unused_caea(self, pos, caea):
        """Informs the given CAEA as unused for the given POS."""

        pos, caea = str(pos), int(caea)

        if caea not in self.db['CAEA_data']:
            raise InvalidRequest(errors=[Error(code='1200',
                                               msg='El codigo de CAEA que se esta informando debe ser del tipo de codigo de autorizacion CAEA')])
        if self.is_caea_used(pos=pos, caea=caea):
            raise InvalidRequest(errors=[Error(code='1202',
                                               msg='El codigo de CAEA que se esta informando fue utilizado en un comprobante para este punto de venta')])

        if self.get_unused_caea(pos=pos, caea=caea) is not None:
            raise InvalidRequest(errors=[Error(code='1209',
                                               msg='El punto de venta informado como sin movimiento ya fue notificado')])

        # marks the CAEA as unused for the given POS
        if caea not in self.db['CAEA_unused']:
            self.db['CAEA_unused'][caea] = {}

        self.db['CAEA_unused'][caea][pos] = self.db['CAEA_data'][caea]

    def is_caea_used(self, pos, caea):
        """Determines whether the given CAEA has been used to authorize any document for the given
        POS."""

        pos, caea = str(pos), int(caea)
        points_of_sale = self.db['CAEA_used'].get(caea, [])
        return pos in points_of_sale

    def get_unused_caea(self, pos, caea):
        """Returns the data of the given CAEA if it was informed as unused for the given POS,
        otherwise returns `None`."""

        pos, caea = str(pos), int(caea)
        return self.db['CAEA_unused'].get(caea, {}).get(pos, None)

    def get_receipt(self, pos, doc_type, doc_num):
        """Returns the generated authorization code and its authorization type (CAE or CAEA) for a
        particular receipt."""

        pos, doc_type, doc_num = str(pos), str(doc_type), int(doc_num)
        return self.db['receipts'][pos][doc_type][doc_num]

    def is_token_expired(self, token):
        """Checks if a fake WSAA token is expired."""

        tributary_id = parse_token(token)
        print ("tributary_id", tributary_id)
        print ("self.db['tokens']", self.db['tokens'])
        # print tributary_id
        # return self.db['tokens'][tributary_id].is_expired
        return False

    def get_last_auth_doc(self, pos, doc_type):
        """Returns the number of the last authorized document for the given document type. If no
        document was authorized yet, returns 0."""

        pos, doc_type = str(pos), str(doc_type)
        return self.db['last_auth_doc'].get(pos, {}).get(doc_type, 0)

    def increment_last_auth_doc(self, pos, doc_type):
        """Increments by 1 the number of the last authorized document."""

        pos, doc_type = str(pos), str(doc_type)
        if pos not in self.db['last_auth_doc']:
            self.db['last_auth_doc'][pos] = {}

        current = self.get_last_auth_doc(pos, doc_type)
        self.db['last_auth_doc'][pos][doc_type] = current + 1

    def get_status(self):
        """Returns the server status"""

        return {
            'app_server': 'OK',
            'db_server': 'OK',
            'auth_server': 'OK',
        }


if __name__ == '__main__':
    host, port = 'localhost', 10000
    server = WSFEv1(host, port, {})

    print 'starting server at', host, port
    server.start()
