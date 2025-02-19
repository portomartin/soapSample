from collections import namedtuple
from lxml import etree
from soap_util import FE, ValidateToken, send_soap_envelope
from errors_utils import InvalidRequest, errors_serialize

import time



@ValidateToken
def FECAEASolicitar(handler, tributary_id):
    """Server handler function that implements the FECAEASolicitar method of the WSFEv1
    web service."""

    ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}
    root = etree.fromstring(handler.body_contents)

    period, fortnight = root.find('.//ar:Periodo', ns).text, root.find('.//ar:Orden', ns).text

    def _result(*elems):
        return FE.FECAEASolicitarResult(
            FE.ResultGet(
                *elems
            )
        )

    try:
        caea_data = handler.server.generate_caea(period=period, fortnight=fortnight)

        caea = FE.CAEA(str(caea_data['CAEA']))
        valid_from = FE.FchVigDesde(caea_data['valid_from'].strftime('%Y%m%d'))
        valid_until = FE.FchVigHasta(caea_data['valid_until'].strftime('%Y%m%d'))
        information_deadline = FE.FchTopeInf(caea_data['information_deadline'].strftime('%Y%m%d'))
        process_datetime = FE.FchProceso(caea_data['processed_datetime'].strftime('%Y%m%d%H%M%S'))
        period = FE.Periodo(period)
        fortnight = FE.Orden(fortnight)

        result = _result(caea, period, fortnight, valid_from, valid_until, information_deadline, process_datetime)
    except InvalidRequest as e:
        period = FE.Periodo('0')
        fortnight = FE.Orden('0')
        errors, observations = errors_serialize(e.errors, e.observations)
        result = _result(period, fortnight, errors, observations)

    payload = FE.FECAEASolicitarResponse(result)

    send_soap_envelope(handler, payload)
