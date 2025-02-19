from lxml import etree
from soap_util import FE, ValidateToken, send_soap_envelope


@ValidateToken
def FECompUltimoAutorizado(handler, tributary_id):
    """Server handler function that implements the FECompUltimoAutorizado method of the WSFEv1
    web service."""

    ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}

    root = etree.fromstring(handler.body_contents)
    POS, doc_type = root.find('.//ar:PtoVta', ns).text, root.find('.//ar:CbteTipo', ns).text

    doc_num = handler.server.get_last_auth_doc(pos=POS, doc_type=doc_type)

    payload = FE.FECompUltimoAutorizadoResponse(
        FE.FECompUltimoAutorizadoResult(
            FE.PtoVta(POS),
            FE.CbteTipo(doc_type),
            FE.CbteNro(str(doc_num))
        )                               
    )

    send_soap_envelope(handler, payload)
