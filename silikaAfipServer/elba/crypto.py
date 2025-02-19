"""
OpenSSL utilities.
"""

from builtins import str
from builtins import object
import os
import subprocess
import tempfile
from future.utils import iteritems

import demo_config


def openssl(command, *args, **params):
    """ Calls openssl's `command` passing `args` separated by spaces and `params` as
    '-param_key param_value'"""
    return OpenSSL(command, *args, **params).communicate()


class OpenSSLError(Exception):
  """Exception class for this module"""
  def __init__(self, returncode, cmd_line, output, error):
    self.returncode = returncode
    self.cmd_line = cmd_line
    self.output = output
    self.error = error

  def __str__(self):
    return "Command '%s' returned non-zero exit status %d\n"\
           "Output: %s\n"\
           "Error: %s" % (self.cmd_line, self.returncode, self.output, self.error)


class OpenSSL(object):
  """Asynchronous handler for a call to an openssl `command` passing `args` separated by spaces and
  `params` as '-param_key param_value'"""
  def __init__(self, command, *args, **params):
    self.popen_args = self._build_args(command, *args, **params)
    self.popen = subprocess.Popen(args=self.popen_args,
                                  shell=True,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=None if demo_config.VERBOSE_TESTS else subprocess.PIPE)

  def _build_args(self, command, *args, **params):
    # wraps the arguments inside quotes to avoid shell errors
    key_params = ['-%s "%s"' % (k, v) for k, v in iteritems(params)]
    normal_params = [str(arg) for arg in args]
    return 'openssl ' + ' '.join([command] + key_params + normal_params)

  def communicate(self, data=None):
    """Passes `data` as stdin to the openssl command and returns the stdout"""
    assert self.popen is not None, 'Should call "async" first'
    rv = self.popen.communicate(data)
    if self.popen.returncode != 0:
      raise OpenSSLError(returncode=self.popen.returncode, cmd_line=self.popen_args, output=rv[0], error=rv[1])
    return rv


def _call_openssl(*args, **kw):
  """Helper function to allow simplify calling the openssl command both with in memory data or in
  file data"""
  assert ('data' in kw and kw['data'] is not None) != ('data_file' in kw and kw['data_file'] is not None),\
         'one and only one of "data" or "data_file" should be given'

  data = kw.get('data', None)
  if 'data_file' in kw and kw['data_file'] is not None:
    args += ('-in %(data_file)s' % kw,)

  del kw['data']
  del kw['data_file']

  openssl_hdlr = OpenSSL(*args, **kw)
  return openssl_hdlr.communicate(data)[0]


def rsa_key_generate(key_length=2048):
  """Generate a new private key"""
  openssl_hdlr = OpenSSL('genrsa', key_length)
  return openssl_hdlr.communicate()[0]


def x509_pem_to_der(cert=None, cert_file=None):
  """Converts an X509 certificate from PEM to DER"""
  return _call_openssl('x509', '-inform pem', '-outform der', data=cert, data_file=cert_file)


def x509_der_to_pem(cert=None, cert_file=None):
  """Converts an X509 certificate from DER to PEM"""
  return _call_openssl('x509', '-inform der', '-outform pem', data=cert, data_file=cert_file)


def x509_subject(cert=None, cert_file=None, inform='pem'):
  """Returns the subject of a certificate."""
  return _call_openssl('x509', '-noout', '-subject', inform=inform, data=cert, data_file=cert_file)

def req_pem_to_der(cert=None, cert_file=None):
  """Converts a certificate signing request from PEM to DER"""
  return _call_openssl('req', '-inform pem', '-outform der', data=cert, data_file=cert_file)


def req_der_to_pem(cert=None, cert_file=None):
  """Converts an certificate signing request from DER to PEM"""
  return _call_openssl('req', '-inform der', '-outform pem', data=cert, data_file=cert_file)


def rsa_der_to_pem(key=None, key_file=None, public=True):
  """Converts an RSA key (public or private) from DER to PEM."""
  args = ['rsa', '-inform der', '-outform pem']
  if public:
    args.append('-pubin')
  return _call_openssl(*args, data=key, data_file=key_file)


def req_gen(key_file=None, subj=None):
  """Generates a certificate signing request with the given key and subject"""
  openssl_hdlr = OpenSSL('req', '-new', key=key_file, subj=subj)
  return openssl_hdlr.communicate()[0]


def smime_verify(smime=None, smime_file=None, inform='pem', CAfile=None):
  """Verifies an S/MIME against the trusted certificates in `CAfile`"""
  assert CAfile is not None, 'CAfile is mandatory'
  return _call_openssl('smime', '-verify', inform=inform, CAfile=CAfile, data=smime, data_file=smime_file)


def smime_decode(smime=None, smime_file=None, inform='pem'):
  """Decodes S/MIME data."""
  return _call_openssl('smime', '-verify', '-noverify', inform=inform, data=smime, data_file=smime_file)


def cms_verify(cms=None, cms_file=None, CAs=None):
  """Verifies a CMS encoded file against a list of Certification Authorities."""
  ca_chain_fname = os.path.join(tempfile.gettempdir(), 'CAChain.pem')
  if CAs is None:
    CAs = []
  try:
    with open(ca_chain_fname, 'wb') as fp:
      for ca in CAs:
        with open(ca, 'rb') as rp:
          fp.write(rp.read())

    return _call_openssl('cms', '-verify', inform='pem', CAfile=ca_chain_fname, data=cms, data_file=cms_file)

  finally:
    os.remove(ca_chain_fname)


def cms_decode(cms=None, cms_file=None):
  """Decodes CMS data."""
  return _call_openssl('cms', '-verify', '-noverify', inform='pem', data=cms, data_file=cms_file)


def cms_get_signer_cert(cms=None, cms_file=None, CAs=None, format='pem', verify=False):
  """Returns the certificates that signed the given CMS. `cms` is the CMS as a string, `CAs` is a
  list with certificate files."""

  ca_chain_fname = os.path.join(tempfile.gettempdir(), 'CAChain.pem')
  signer_fname = os.path.join(tempfile.gettempdir(), 'signer.pem')

  if CAs is None:
    CAs = []

  try:
    with open(ca_chain_fname, 'wb') as fp:
      for ca in CAs:
        with open(ca, 'rb') as rp:
          fp.write(rp.read())

    args = ['cms', '-verify'] + ([] if verify else ['-noverify'])
    _call_openssl(*args, inform=format, CAfile=ca_chain_fname, data=cms, data_file=cms_file, signer=signer_fname)

    with open(signer_fname, 'rb') as fp:
      return fp.read()

  finally:
    os.remove(ca_chain_fname)
    try:
      os.remove(signer_fname)
    except:
      # if OpenSSL fails the file is deleted
      pass


def cms_sign(data=None, data_file=None, signer=None, inkey=None, outform='pem'):
  """Encodes some data in CMS format."""
  assert signer is not None, 'signer is mandatory'
  assert inkey is not None, 'inkey is mandatory'
  return _call_openssl('cms', '-sign', '-nodetach', signer=signer, inkey=inkey, outform=outform, data=data, data_file=data_file)


if __name__ == '__main__':
  sample_cert_path = demo_config.config_rel_path_to_abs(demo_config.CERT_FILE)

  # most basic test: certificate checking using both APIs
  h = OpenSSL('x509', '-text', '-noout', '-in '+sample_cert_path)
  h.communicate()
  openssl('x509', '-text', '-noout', '-in '+sample_cert_path)

  with open(sample_cert_path, 'rb') as f:
    cert = f.read()

  # certificate checking using stdin
  h = OpenSSL('x509', '-text', '-noout')
  h.communicate(cert)

  # key generation test
  key = rsa_key_generate()

  key_file = os.path.join(tempfile.gettempdir(), 'key')
  with open(key_file, 'wb') as f:
    f.write(key)

  subj = '/C=AR/ST=BsAs/O=Epson/CN=test'

  # CSR generation test
  csr = req_gen(key_file=key_file, subj=subj)

  # CSR formatting test
  assert csr == req_der_to_pem(req_pem_to_der(cert=csr))

  # creates a self signed certificate from the previous CSR and key
  h = OpenSSL('req', '-x509', '-batch', days=365, key=key_file)
  cert = h.communicate(csr)[0]

  # X509 certificate formatting test
  assert cert == x509_der_to_pem(x509_pem_to_der(cert=cert))

  signer_file = os.path.join(tempfile.gettempdir(), 'signer.cert')
  with open(signer_file, 'wb') as f:
    f.write(cert)

  # CMS tests
  cms = cms_sign(data='nobody expects the Spanish inquisition', signer=signer_file, inkey=key_file)
  cms_verify(cms=cms, CAs=[signer_file])
  cms_decode(cms=cms)
