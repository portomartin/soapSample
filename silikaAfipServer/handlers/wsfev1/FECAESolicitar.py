from lxml import etree
from soap_util import FE, ValidateToken, current_datetime, send_soap_envelope, InvalidReceiptNumber
from errors_utils import InvalidRequest, errors_serialize



class MissingField(Exception):
    pass


def _build_FECAESolicitar_response(server,
                                   tributary_id,
                                   pos,
                                   doc_type,
                                   rec_count,
                                   process_datetime,
                                   result,
                                   FECAEDetResponse):
    """Returns a string containing the response of the `FECAESolicitar` SOAP method.
    `rec_count` is the number of receipts that the user attempted to authorize.
    `FECAEDetResponse` is an `lxml` element containing the information to dump inside the
    `FeDetResp` XML element (be it an error, observation or success response)."""

    assert result in ('A', 'R'), result

    return FE.FECAESolicitarResponse(
        FE.FECAESolicitarResult(
            FE.FeCabResp(
                FE.Cuit(tributary_id),
                FE.PtoVta(pos),
                FE.CbteTipo(str(doc_type)),
                FE.FchProceso(process_datetime.strftime('%Y%m%d%H%M%S')),
                FE.CantReg(str(rec_count)),
                FE.Resultado(result),
                FE.Reproceso('N')  # unused
            ),
            FE.FeDetResp(FECAEDetResponse)
        )
    )


def _fecae_solicitar_process_req(server, req, pos, doc_type):
    try:
        ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}

        customer_tributary_id_type = req.find('ar:DocTipo', ns).text
        customer_tributary_id = req.find('ar:DocNro', ns).text

        doc_from, doc_until = req.find('ar:CbteDesde', ns).text, req.find('ar:CbteHasta', ns).text
        doc_date = req.find('ar:CbteFch', ns).text

        assert doc_from == doc_until, 'Only single document requests supported'

        def _response(result, *elems):
            assert result in ('A', 'R')

            return FE.FECAEDetResponse(
                FE.Concepto('1'),  # TODO: where does this this field come from?
                FE.DocTipo(customer_tributary_id_type),
                FE.DocNro(customer_tributary_id),
                FE.CbteDesde(doc_from),
                FE.CbteHasta(doc_from),  # TODO: handle batch?
                FE.CbteFch(doc_date),
                FE.Resultado(result),
                *elems
            )

        authorized_receipt = server.authorize_receipt(pos=pos, doc_type=doc_type, doc_num=int(doc_from), receipt=req, xml_namespace=ns)

        return _response('A', FE.CAE(str(authorized_receipt['authorization_code'])), FE.CAEFchVto(authorized_receipt['due_date'].strftime('%Y%m%d'))), \
               'A', \
               authorized_receipt['process_datetime']
    except InvalidReceiptNumber:
        errors = FE.Errors(
            FE.Err(
                FE.Code('10016'),
                FE.Msg('El numero o fecha del comprobante no se corresponde con el proximo a autorizar. ' + \
                       'Consultar metodo FECompUltimoAutorizado.')
            )
        )
        return _response('R', errors), 'R', server.get_datetime()
    except InvalidRequest as e:
        errors, observations = errors_serialize(e.errors, e.observations)
        return _response('R', errors, observations), 'R', server.get_datetime()
    except AttributeError:
        # probably caused by a missing tag (and attempted to access the `.text` a None)
        # TODO: check the actual error from WSFEv1 and return it
        raise MissingField()


@ValidateToken
def FECAESolicitar(handler, tributary_id):
    """Server handler function that implements the FECAESolicitar method of the WSFEv1
    web service."""

    ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}
    root = etree.fromstring(handler.body_contents)

    header, detail = root.find('.//ar:FeCabReq', ns), root.find('.//ar:FeDetReq', ns)
    doc_type, POS = header.find('ar:CbteTipo', ns).text, header.find('ar:PtoVta', ns).text

    rec_count = header.find('ar:CantReg', ns).text
    assert rec_count == '1', rec_count  # we accept just a single document in the request for now

    req = detail.find('ar:FECAEDetRequest', ns)

    fecae_det_response, result, process_datetime = _fecae_solicitar_process_req(handler.server, req, POS, doc_type)
    body = _build_FECAESolicitar_response(server=handler.server,
                                          tributary_id=tributary_id,
                                          pos=POS,
                                          doc_type=doc_type,
                                          rec_count=1,
                                          process_datetime=process_datetime,
                                          result=result,
                                          FECAEDetResponse=fecae_det_response)
    send_soap_envelope(handler, body)
