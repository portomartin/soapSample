import re
import sys
import argparse


# address where the commands will be directed
# the protocol part of the URL can be one of http, https, serial or usb.
# in case of serial, the address itself has to be the name of the serial port, 
# e.g.: COM1, /dev/ttyUSB0, /dev/ttyS2, etc.
# in case of USB, the address part is ignored.
BASE_URL = 'https://localhost:4433'

# whether to be verbose when executing tests
VERBOSE_TESTS = False

# protocol to be used when communicating
# (only JSON is supported for the moment)
PROTOCOL = 'json'

# default communication protocol (supported: rest|ext)
DEF_COMM_PROT = 'rest'

# the baudrate used when the communication is through the serial port
SERIAL_BAUDRATE = 115200

# the type of display communication 
DISPLAY_COMM = 'display_comm_serial'

# directory where the binaries of the application need to be stored (for
# multi-execution tests)
BIN_DIR = '../../target'

# default binary to use when for automatic executions
BIN_NAME = 'elba.pc'

# files storing the state of the application (for multi-execution tests)
DB_FILES = ['db.sqlite', 'db.sqlite-wal', 'db.sqlite-shm', 'block_info', 'fmm', 'sc']

# file containing the private key used for client authentication
KEY_FILE = '../../dev/app/epson_remote.pem'

# file containing the client certificate
CERT_FILE = '../../dev/app/epson_remote.pem'

# files with trusted certification authorities used to verify the server's certificate
CA_CERT_FILES = '../../dev/app/root.crt'

# limit of concurrent commands supported
MAX_CONCUR_CMDS = 5

# extra HTTP headers to include in the requests
HTTP_EXTRA_HEADERS = {}


def config_rel_path_to_abs(rel_path):
  """Converts a path relative to the configuration file into an absolute path"""
  from os import path
  return path.join(path.dirname(path.abspath(__file__)), rel_path)


# project_config.py file is meant to redefine demo_config.py values in each project
try:
    from project_config import *
except ImportError:
    # it's not an error if the file is not present
    pass

# if the file local_config.py is present, it overrides this configuration
try:
    from local_config import *
except ImportError:
    # it's not an error if the file is not present
    pass
finally:
    # Allow passing of arguments in python scripts to 
    # supersede global() values
    parser = argparse.ArgumentParser(add_help=False)
    # Using parse_known_args instead of parse_args 
    # allows arbitrary values to be passed
    args, other = parser.parse_known_args()
    for x in other:
        if re.match(r'[-\w]+=[^=\s]+$', x):
            key, value = x.split("=")
            # We'll use the common syntax --VAR-NAME 
            # and translate it to VAR_NAME
            key = key.strip("-").replace("-", "_")
            globals()[key] = value
