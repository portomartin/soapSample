from lxml import etree
from soap_util import FE, ValidateToken, send_soap_envelope, InvalidReceiptNumber
from errors_utils import InvalidRequest, errors_serialize, Error



class MissingField(Exception):
    pass


def _build_FECAEARegInformativo_response(server,
                                         tributary_id,
                                         pos,
                                         doc_type,
                                         rec_count,
                                         process_datetime,
                                         result,
                                         FECAEADetResponse):
    """Returns a string containing the response of the `FECAEARegInformativo` SOAP method.
    `rec_count` is the number of receipts that the user attempted to authorize.
    `FECAEADetResponse` is an `lxml` element containing the information to dump inside the
    `FeDetResp` XML element (be it an error, observation or success response)."""

    assert result in ('A', 'R'), result

    return FE.FECAEARegInformativoResponse(
        FE.FECAEARegInformativoResult(
            FE.FeCabResp(
                FE.Cuit(tributary_id),
                FE.PtoVta(pos),
                FE.CbteTipo(str(doc_type)),
                FE.FchProceso(process_datetime.strftime('%Y%m%d%H%M%S')),
                FE.CantReg(str(rec_count)),
                FE.Resultado(result),
                FE.Reproceso('N')  # unused
            ),
            FE.FeDetResp(FECAEADetResponse)
        )
    )


def _fecaea_reg_informativo_process_req(server, req, pos, doc_type):
    try:
        ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}

        customer_tributary_id_type = req.find('ar:DocTipo', ns).text
        customer_tributary_id = req.find('ar:DocNro', ns).text

        doc_from, doc_until = req.find('ar:CbteDesde', ns).text, req.find('ar:CbteHasta', ns).text
        doc_date = req.find('ar:CbteFch', ns).text
        caea = req.find('ar:CAEA', ns).text

        assert doc_from == doc_until, 'Only single document requests supported'

        def _response(result, *elems):
            assert result in ('A', 'R')

            return FE.FECAEADetResponse(
                FE.Concepto('1'),  # TODO: where does this this field come from?
                FE.DocTipo(customer_tributary_id_type),
                FE.DocNro(customer_tributary_id),
                FE.CbteDesde(doc_from),
                FE.CbteHasta(doc_from),  # TODO: handle batch?
                FE.CbteFch(doc_date),
                FE.Resultado(result),
                *elems
            )

        # checks the receipt generation datetime is sent for contingency mode
        if req.find('ar:CbteFchHsGen', ns) is None:
            raise InvalidRequest(errors=[Error(code='1440',
                                               msg='El campo CbteFchHsGen es obligatorio informarlo ' + \
                                                   'cuando el punto de venta es del tipo CONTINGENCIA CAEA')])

        informed_receipt = server.inform_receipt(pos=pos, doc_type=doc_type, doc_num=int(doc_from), caea=caea, receipt=req, xml_namespace=ns)

        return _response('A', FE.CAEA(str(informed_receipt['authorization_code']))), 'A', informed_receipt['process_datetime']
    except InvalidReceiptNumber:
        errors = FE.Errors(
            FE.Err(
                FE.Code('703'),
                FE.Msg('El numero de comprobante informado debe ser mayor en 1 al ultimo informado ' + \
                       'para igual punto de venta y tipo de comprobante. Consultar metodo FECompUltimoAutorizado.')
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
def FECAEARegInformativo(handler, tributary_id):
    """Server handler function that implements the FECAEARegInformativo method of the WSFEv1
    web service."""

    ns = {'ar': 'http://ar.gov.afip.dif.FEV1/'}
    root = etree.fromstring(handler.body_contents)

    header, detail = root.find('.//ar:FeCabReq', ns), root.find('.//ar:FeDetReq', ns)
    doc_type, POS = header.find('ar:CbteTipo', ns).text, header.find('ar:PtoVta', ns).text

    rec_count = header.find('ar:CantReg', ns).text
    assert rec_count == '1', rec_count  # we accept just a single document in the request for now

    req = detail.find('ar:FECAEADetRequest', ns)

    fecae_det_response, result, process_datetime = _fecaea_reg_informativo_process_req(handler.server, req, POS, doc_type)
    body = _build_FECAEARegInformativo_response(server=handler.server,
                                                tributary_id=tributary_id,
                                                pos=POS,
                                                doc_type=doc_type,
                                                rec_count=1,
                                                process_datetime=process_datetime,
                                                result=result,
                                                FECAEADetResponse=fecae_det_response)
    send_soap_envelope(handler, body)
