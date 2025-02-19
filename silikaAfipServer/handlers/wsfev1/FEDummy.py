from lxml import etree
from soap_util import FE, send_soap_envelope


def FEDummy(handler):
    """Server handler function that implements the FEDummy method of the WSFEv1
    web service."""

    server_status = handler.server.get_status()

    payload = FE.FEDummyResponse(
        FE.FEDummyResult(
            FE.AppServer(server_status['app_server']),
            FE.DbServer(server_status['db_server']),
            FE.AuthServer(server_status['auth_server'])
        )
    )

    send_soap_envelope(handler, payload)
