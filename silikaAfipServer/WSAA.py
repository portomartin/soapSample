import elba
import cert_utils

from http_server import Server
from handlers.wsaa import LoginCms, TokenData, LoginInvalidRequest, build_token, parse_token


# configuration file to use for the certificate authority. Note that the CA directory is left to be
# set at the time of initialization.
CONFIG_FILE = """[ ca ]
default_ca       = CA_WSAA                # The default ca section

[ CA_WSAA ]

dir              = %(dir_path)r           # top dir
database         = $dir/index.txt         # index file
new_certs_dir    = $dir/newcerts          # new certs dir

certificate      = $dir/cacert.pem        # the CA cert
serial           = $dir/serial            # serial number file
private_key      = $dir/private/cakey.pem # CA private key
RANDFILE         = $dir/private/.rand     # random number file

default_days     = 365                    # how long to certify for
default_crl_days = 30                     # how long before next CRL
default_md       = default                # md to use

policy           = wsaa_policy            # default policy
email_in_dn      = no                     # don't add the email into cert DN

name_opt         = ca_default             # subject name display option
cert_opt         = ca_default             # certificate display option
copy_extensions  = none                   # don't copy extensions from request

[ wsaa_policy ]
# if the value is "match" then the field value must match the same field in the
# CA certificate. If the value is "supplied" then it must be present.
# Optional means it may be present. Any fields not mentioned are silently
# deleted.
countryName            = supplied
stateOrProvinceName    = optional
organizationName       = supplied
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional
serialNumber           = optional

[ v3_ca ]

# Extensions for a typical CA

# PKIX recommendation.

subjectKeyIdentifier=hash

authorityKeyIdentifier=keyid:always,issuer

basicConstraints = critical,CA:true
"""


class WSAA(Server):
    """Fake server to simulate some functionality from the WSAA. `db` is dict where all the
    state of the server is stored."""

    def __init__(self, host, port, db):
        POST_handlers = {'/ws/services/LoginCms': LoginCms}
        GET_handlers = {}

        self._ca = cert_utils.CertificateAuthority(name='WSAA', config_file=CONFIG_FILE, policy='wsaa_policy')
        self._ca.create()

        self._db = db

        # maps valid tokens to the corresponding tributary IDs (CUIT)
        self._db['tokens'] = self._db.get('tokens', {})

        # calls the parent constructor with the handlers to simulate the WSAA
        Server.__init__(self, host, port, GET_handlers, POST_handlers)

    def sign_cert(self, csr):
        """Returns an X.509 certificate from the given `csr` (PEM string) and registers it in
        the internal DB so calls to LoginCms are authorized."""

        return self._ca.auth_csr_pem(csr)

    def create_token(self, tributary_id, is_expired=False):
        """Creates a token that clients can use to authenticate."""

        token, sign = build_token(tributary_id)
        self._db['tokens'][tributary_id] = TokenData(token, sign, is_expired)
        return token, sign

    def expire_token(self, tributary_id):
        """Marks the token issued for the corresponding `tributary_id` as expired."""

        token_data = self._db['tokens'][tributary_id]
        self._db['tokens'][tributary_id] = token_data._replace(is_expired=True)

    def get_ca_cert(self):
        return self._ca._cert


if __name__ == '__main__':
    host, port = 'localhost', 9999
    server = WSAA(host, port)

    print 'starting server at', host, port
    server.start()
