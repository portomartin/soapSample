from lxml import etree
from soap_util import FE, ValidateToken, send_soap_envelope
from errors_utils import InvalidRequest, errors_serialize

import time


@ValidateToken
def FECAEAConsultar(handler, tributary_id):
    """Server handler function that implements the FECAEAConsultar method of the WSFEv1
    web service."""

    ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}
    root = etree.fromstring(handler.body_contents)

    period, fortnight = root.find('.//ar:Periodo', ns).text, root.find('.//ar:Orden', ns).text

    def _result(*elems):
        return FE.FECAEAConsultarResult(
            FE.ResultGet(
                *elems
            )
        )

    try:
        caea_data = handler.server.retrieve_existent_caea(period=period, fortnight=fortnight)

        result = _result(FE.CAEA(str(caea_data['CAEA'])),
                         FE.Periodo(period),
                         FE.Orden(fortnight),
                         FE.FchVigDesde(caea_data['valid_from'].strftime('%Y%m%d')),
                         FE.FchVigHasta(caea_data['valid_until'].strftime('%Y%m%d')),
                         FE.FchTopeInf(caea_data['information_deadline'].strftime('%Y%m%d')),
                         FE.FchProceso(caea_data['processed_datetime'].strftime('%Y%m%d%H%M%S')))
    except InvalidRequest as e:
        errors, observations = errors_serialize(e.errors, e.observations)
        result = _result(FE.Periodo(period),
                         FE.Orden(fortnight),
                         errors,
                         observations)

    payload = FE.FECAEAConsultarResponse(result)

    send_soap_envelope(handler, payload)
