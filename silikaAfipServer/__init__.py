from WSAA import WSAA, LoginInvalidRequest
from WSFEv1 import WSFEv1, get_caea_dates, Error, Observation, InvalidRequest
from contextlib import contextmanager
from psutil import process_iter
from signal import SIGKILL

DEFAULT_WSAA_PORT, DEFAULT_WSFE_PORT = 9999, 10000

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

@contextmanager
def start_services(wsaa_port=DEFAULT_WSAA_PORT, wsfe_port=DEFAULT_WSFE_PORT, db=None):
	"""Context manager that starts WSAA and WSFEv1 instances and shuts them down when
	finished. This function accepts the ports where the services will be listening and an optional
	external DB (a regular python dict) to persist state between executions."""

	# shared DB
	db = {} if db is None else db

	wsaa, wsfe = WSAA('0.0.0.0', wsaa_port, db), WSFEv1('0.0.0.0', wsfe_port, db)

	wsaa.start()
	wsfe.start()

	try:
		yield wsaa, wsfe
	finally:
		wsaa.stop()
		wsfe.stop()

def kill_server():
	for proc in process_iter():
		for conns in proc.get_connections(kind='inet'):
			if conns.laddr[1] == DEFAULT_WSAA_PORT:
				proc.send_signal(SIGKILL) 
				continue
				
	for proc in process_iter():
		for conns in proc.get_connections(kind='inet'):
			if conns.laddr[1] == DEFAULT_WSFE_PORT:
				proc.send_signal(SIGKILL) 
				continue

if __name__ == '__main__':
	import time

	kill_server()
	
	with start_services() as (wsaa, wsfe):
	
		flag = '\x1b[6;33;40m' + u'\u2588' + '\x1b[6;34;40m' + u'\u2588' + '\x1b[6;31;40m' + u'\u2588' + '\x1b[6;30;47m'
		color = '\x1b[6;30;47m'
		no_color = '\x1b[0m'
		padd = 50
	
		print ''
		print color + '-------------------------------------------'.ljust(padd) + no_color
		print color + ' AFIP | eInvoice Fake Server | version 1.0 '+ flag.ljust(padd-6) + no_color
		print color + '-------------------------------------------'.ljust(padd) + no_color
		print color + format(wsaa.url).ljust(padd) + no_color
		print color + format(wsfe.url).ljust(padd) + no_color
		print color + '-------------------------------------------'.ljust(padd) + no_color
		print ''
		
		while True:
			time.sleep(5)

