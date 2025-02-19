import re
import crypto
import random
import xml.etree.ElementTree as ET

from base64 import b64encode, b64decode
from datetime import timedelta
from test_utils import current_datetime
from collections import namedtuple


# regular expression to extract the CUIT from a certificate's subject
CUIT_FROM_SUBJ_RE = re.compile(r'CUIT (\d+)')


# token representation in the service database
TokenData = namedtuple('TokenData', 'tributary_id, dummy, is_expired')


class LoginInvalidRequest(Exception):
    """Used to create responses that simulate an AFIP's `loginCms` error."""

    def __init__(self, code=None, msg=None):
        self.code = code
        self.msg = msg

        _msg = ''
        if self.code is not None:
            _msg += 'Code: %s' % self.code
        if self.msg is not None:
            _msg += '\nMessage: %s' % self.msg

        Exception.__init__(self, msg)


def _parse_tributary_id(cert_subject):
    """Parses the tributary ID from an X.509 certificate's subject."""

    return CUIT_FROM_SUBJ_RE.search(cert_subject).group(1)


def _extract_cert_from_soap(soap_str, ca_cert_file):
    """Parses a SOAP envelope for the WSAA LoginCms method and returns the CMS signer cert.
    `soap_str` is the SOAP request as a string and `ca_cert_file` is the file name of the
    certificate used to validate the CMS."""

    root = ET.fromstring(soap_str)

    ns = {'afip': 'http://wsaa.view.sua.dvadac.desein.afip.gov'}
    cms_elem = root.find('.//afip:in0', ns)
    cms = b64decode(cms_elem.text)

    # TODO: would it be necessary to actually verify the certificate?
    return crypto.cms_get_signer_cert(cms=cms, CAs=[ca_cert_file], format='der', verify=False)


def LoginCms(handler, query_params, path_params):
    """Simulates the LoginCms SOAP method from AFIP's WSAA."""

    signer_cert = _extract_cert_from_soap(handler.body_contents, handler.server.get_ca_cert())
    subject = crypto.x509_subject(signer_cert)

    tributary_id = _parse_tributary_id(subject)

    # TODO: appending the milliseconds in the time zone as a workaround. The milliseconds are
    #       included in the real WSAA response, so we must make it as real as we can
    generation_time = current_datetime(timezone='.000-03:00')
    expiration_time = current_datetime(timezone='.000-03:00', offset=timedelta(hours=12))

    try:
        token, sign = handler.server.create_token(tributary_id)
        unique_id = random.randint(0, 1e9)

        handler.send_response(200)
        handler.end_headers()
        handler.wfile.write("""
            <?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <soapenv:Body>
                    <loginCmsResponse xmlns="http://wsaa.view.sua.dvadac.desein.afip.gov">
                        <loginCmsReturn>&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot; standalone=&quot;yes&quot;?&gt;
            &lt;loginTicketResponse version=&quot;1.0&quot;&gt;
                &lt;header&gt;
                    &lt;source&gt;CN=wsaahomo, O=AFIP, C=AR, SERIALNUMBER=CUIT 33693450239&lt;/source&gt;
                    &lt;destination&gt;SERIALNUMBER=CUIT %(tributary_id)s, CN=einvoice1&lt;/destination&gt;
                    &lt;uniqueId&gt;%(unique_id)s&lt;/uniqueId&gt;
                    &lt;generationTime&gt;%(generation_time)s&lt;/generationTime&gt;
                    &lt;expirationTime&gt;%(expiration_time)s&lt;/expirationTime&gt;
                &lt;/header&gt;
                &lt;credentials&gt;
                    &lt;token&gt;%(token)s&lt;/token&gt;
                    &lt;sign&gt;%(sign)s&lt;/sign&gt;
                &lt;/credentials&gt;
            &lt;/loginTicketResponse&gt;
                        </loginCmsReturn>
                    </loginCmsResponse>
                </soapenv:Body>
            </soapenv:Envelope>""" % locals())
    except LoginInvalidRequest as e:
        code = e.code
        string = e.msg

        handler.send_response(500)
        handler.end_headers()
        handler.wfile.write("""
            <?xml version="1.0" encoding="utf-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <soapenv:Body>
                    <soapenv:Fault>
                        <faultcode>%(code)s</faultcode>
                        <faultstring>%(string)s</faultstring>
                        <detail />
                    </soapenv:Fault>
                </soapenv:Body>
            </soapenv:Envelope>
            """ % locals())

    return True
