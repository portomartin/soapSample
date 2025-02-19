from lxml import etree
from soap_util import FE, ValidateToken, send_soap_envelope


@ValidateToken
def FECompConsultar(handler, tributary_id):
    """Server handler function that implements the FECompConsultar method of the WSFEv1
    web service."""

    ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}

    root = etree.fromstring(handler.body_contents)
    POS, doc_type, doc_num = root.find('.//ar:PtoVta', ns).text, root.find('.//ar:CbteTipo', ns).text, root.find('.//ar:CbteNro', ns).text
    # TODO: handle nonexistent receipt
    authorized_receipt = handler.server.get_receipt(pos=POS, doc_type=doc_type, doc_num=doc_num)

    payload = FE.FECompConsultarResponse(
        FE.FECompConsultarResult(
            FE.ResultGet(
                # TODO: add the remaining fields
                FE.CbteDesde(doc_num),
                FE.CbteHasta(doc_num),
                FE.CodAutorizacion(str(authorized_receipt['authorization_code'])),
                FE.EmisionTipo(authorized_receipt['authorization_type']),
                FE.FchVto(authorized_receipt['due_date'].strftime('%Y%m%d')),
                FE.FchProceso(authorized_receipt['process_datetime'].strftime('%Y%m%d%H%M%S')),
                FE.PtoVta(POS),
                FE.CbteTipo(doc_type)
            )
        )
    )

    send_soap_envelope(handler, payload)
