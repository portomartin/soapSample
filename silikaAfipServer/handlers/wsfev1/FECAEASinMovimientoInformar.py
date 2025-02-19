from lxml import etree
from soap_util import FE, ValidateToken, send_soap_envelope
from errors_utils import InvalidRequest, errors_serialize
from datetime import datetime


@ValidateToken
def FECAEASinMovimientoInformar(handler, tributary_id):
    """Server handler function that implements the FECAEASinMovimientoInformar method of the WSFEv1
    web service."""

    ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}
    root = etree.fromstring(handler.body_contents)

    pos, caea = root.find('.//ar:PtoVta', ns).text, root.find('.//ar:CAEA', ns).text

    def _result(caea, pos, operation_result, *elems):
        return FE.FECAEASinMovimientoResult(
            FE.CAEA(caea),
            FE.PtoVta(pos),
            FE.Resultado(operation_result),
            *elems
        )

    try:
        handler.server.inform_unused_caea(pos=pos, caea=caea)

        process_datetime = FE.FchProceso(handler.server.get_datetime().strftime('%Y%m%d%H%M%S'))
        operation_result = 'A'

        result = _result(caea, pos, operation_result, process_datetime)
    except InvalidRequest as e:
        errors, observations = errors_serialize(e.errors, e.observations)
        operation_result = 'R'
        result = _result(caea, pos, operation_result, errors, observations)

    payload = FE.FECAEASinMovimientoResponse(result)

    send_soap_envelope(handler, payload)
