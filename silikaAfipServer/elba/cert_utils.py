"""
Utility functions to handle certificates.
"""

import base64
import os
import shutil
import tempfile
from future.utils import iteritems
from collections import namedtuple

import certs_data
import crypto


ConfigFile = namedtuple('ConfigFile', 'file_name, contents')


FILE_PATH = tempfile.gettempdir()

# TODO: this should come from the general settings
CA_BASE_PATH = FILE_PATH


START_DATE = '140101000000Z'
END_DATE = '241231235959Z'


class ChDir(object):
    def __init__(self, path):
        self.path = path
        self.old_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.old_path)


class CertificateAuthority(object):
    """
    Certificate authority
    Uses openssl's ca implementation. Optionally a specific configuration can be used.
    `name` is the unique identifier to the CA (folder where the dir
    structure is located)
    `path` is the path to the folder containing the CA.
    `config_file` is the configuration file to use for the CA, or `None` to use the default one. The
    CA's top directory field in the configuration file must be a variable called `dir_path` that
    will be replaced at initialization.
    `policy` indicates the CA policy to use.
    """

    def __init__(self, name, path=CA_BASE_PATH, config_file=None, policy='policy_anything'):
        self.name = name
        self._path = os.path.abspath(os.path.join(path, name))
        self._ca_path = os.path.abspath(os.path.join(self._path, 'demoCA'))
        self._key = os.path.abspath(os.path.join(self._ca_path, 'private', 'cakey.pem'))
        self._cert = os.path.abspath(os.path.join(self._ca_path, 'cacert.pem'))
        self._config =  ConfigFile('ca.cnf', config_file % { 'dir_path': self._ca_path }) if config_file is not None else None
        self._policy = policy

    def create(self, startdate=START_DATE, enddate=END_DATE, key=None, cacert=None):
        """Creates a new certificate authority.
        If key and certificate are given, those are moved and used for the CA.
        If not, they are both created from scratch."""

        # in case it already existed
        self.delete()
        self.create_folders()

        with open(os.path.join(self._ca_path, 'serial'), 'wb') as fp:
            fp.write('01')
        open(os.path.join(self._ca_path, 'index.txt'), 'wb').close()

        if key is not None:
            with open(self._key, 'wb') as f:
                f.write(key)
        else:
            assert cacert is None, 'Private key missing'
            with open(self._key, 'wb') as f:
                f.write(crypto.rsa_key_generate())

        if self._config is not None:
            with open(os.path.abspath(os.path.join(self._path, self._config.file_name)), 'wb') as fp:
                fp.write(self._config.contents)

        if cacert is not None:
            with open(self._cert, 'wb') as f:
                f.write(cacert)
        else:
            # this operation needs to be done in the CA's folder
            with ChDir(self._path):
                with open('ca.csr', 'wb') as f:
                    f.write(new_csr(key_file=self._key, CN=self.name))
                args = [
                    '-selfsign',
                    '-batch',
                    '-in ca.csr',
                    '-extensions v3_ca',
                ]
                if self._config is not None:
                    args.append('-config %s' % self._config.file_name)

                crypto.openssl('ca',
                               *args,
                               out=self._cert,
                               keyfile=self._key,
                               startdate=startdate,
                               enddate=enddate,
                               policy=self._policy)

        return self

    def new_cert_n_key(self,
                       date_from=START_DATE,
                       date_until=END_DATE,
                       CN='EaglePlus',
                       is_CA=False):
        """Creates a new certificate from scratch using a new private key.
        Use `auth_csr_pem` if you need to use a specific key.
        `params` are sent directly to openssl as '-key value'.
        """

        rsa_key = crypto.rsa_key_generate()
        csr_pem = new_csr(key=rsa_key, CN=CN)

        self.reset_db()
        cert_pem = self.auth_csr_pem(csr_pem=csr_pem,
                                     startdate=date_from,
                                     enddate=date_until,
                                     is_CA=is_CA)

        return cert_pem, rsa_key

    def get_new_CA(self, CN, startdate=START_DATE, enddate=END_DATE):

        key = crypto.rsa_key_generate()
        csr_pem = new_csr(key=key, CN=CN)

        self.reset_db()
        cert_pem = self.auth_csr_pem(csr_pem=csr_pem, is_CA=True, startdate=startdate, enddate=enddate)

        return CertificateAuthority(name=CN).create(key=key, cacert=cert_pem)

    def auth_csr_pem(self, csr_pem, is_CA=False, **params):
        with ChDir(self._path):
            # WARNING: Do not name the filename with just AUX.csr or AUX.*
            # since Windows considers it a reserved name the same way it does for PRN, CON, NUL
            aux_csr = 'myaux.csr'
            aux_pem = 'myaux.pem'
            with open(aux_csr, 'wb') as f:
                f.write(csr_pem)
            args = [
                '-batch',
                '-noemailDN',
                '-in {0}'.format(aux_csr),
                '-out {0}'.format(aux_pem)
            ]
            if is_CA:
                args.append('-extensions v3_ca')
            if self._config is not None:
                args.append('-config %s' % self._config.file_name)

            default_params = {
                'startdate': START_DATE,
                'enddate': END_DATE,
                'policy': self._policy,
            }
            # replace default or add user parameters
            default_params.update(params)

            crypto.openssl('ca', *args, **default_params)

            with open(aux_pem, 'rb') as f:
                return f.read()

    def auth_csr_der(self, csr_der, is_CA=False, **params):
        csr_pem = crypto.req_der_to_pem(cert=csr_der)
        return self.auth_csr_pem(csr_pem=csr_pem, is_CA=is_CA, **params)

    def cms(self, data):
        return crypto.cms_sign(data=data, signer=self._cert, inkey=self._key)

    def reset_db(self):
        open(os.path.join(self._ca_path, 'index.txt'), 'wb').close()

    def create_folders(self):
        paths = [
            self._path,
            os.path.join(self._ca_path, 'private'),
            os.path.join(self._ca_path, 'newcerts'),
        ]
        for path in paths:
            if os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path)

    def delete(self):
        if os.path.exists(self._path):
            shutil.rmtree(self._path)


def new_csr(key=None, key_file=None, **subj):
    """Make a CSR for the specified key. Additional parameters are used
    as subject."""

    assert (key is None) != (key_file is None), 'one and only one of "key" or "key_file" should be given'

    if key_file is None:
        key_file = os.path.join(FILE_PATH, 'key.pem')
        with open(key_file, 'wb') as f:
            f.write(key)

    data = {'C': 'AR', 'ST': 'BsAs', 'O': 'Epson', 'CN': ''}
    data.update(subj)
    data = '/'.join('%s=%s' % (k, v) for k, v in iteritems(data) if v)
    subj = '/%s/' % data
    return crypto.req_gen(key_file=key_file, subj=subj)


def generate_CA_chain(path=CA_BASE_PATH):
    """Generates a certificate authority chain."""

    # creates the root authority (self signed)
    root = CertificateAuthority(name='root', path=path)
    root.create(key=certs_data.ROOT2_KEY, cacert=certs_data.ROOT2_CERT)

    # creates the intermediate authority
    interm = CertificateAuthority(name='interm', path=path)
    interm.create(key=certs_data.INT2A_KEY, cacert=certs_data.INT2A_CERT)

    return root, interm


def delete_CA_chain(path=CA_BASE_PATH):
    """Deletes the certificate authority chain."""

    root = CertificateAuthority(name='root', path=path).delete()
    interm = CertificateAuthority(name='interm', path=path).delete()


def auth_csr_der(csr_data):
    """Returns an authorized certificate for the given CSR."""

    # generates all the CA chain
    root, interm = generate_CA_chain()

    # gets the authorized certificate from the CSR
    cert_data = interm.auth_csr_der(csr_data)

    # deletes the CA chain
    delete_CA_chain()

    return cert_data


def prepare_cert(cert=None, cert_file=None):
    """Converts a PEM cert to a base 64 encoded DER."""
    data = crypto.x509_pem_to_der(cert=cert, cert_file=cert_file)
    return base64.b64encode(data)


if __name__ == '__main__':
    test_root_ca = CertificateAuthority(name='testRootCA').create()
    test_interm_ca = test_root_ca.get_new_CA(CN='testIntermCA')
