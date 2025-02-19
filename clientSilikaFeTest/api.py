import json
import requests 
from random import randrange
import pprint
import csv
import sys
from psutil import process_iter
from signal import SIGKILL
	
from base64 import b64decode, b64encode
from os import path

sys.path.append('/mnt/sdc/silika/test/integration/arg/')

import einvoice

# globals
API_ENDPOINT = "http://127.0.0.1:8000"
API_ENDPOINT = "https://127.0.0.1:4433"
API_HOST_SID = "3IprLInY3uRqF1++uSpVx0CIH8lA/55j"

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# ---------
# post
# ---------
def post(endpoint, data):

	global API_HOST_SID
	url = API_ENDPOINT + endpoint

	print_request ("post", endpoint)
	r = requests.post(url = url, json=data, verify=False, cookies={"__Host-sid": API_HOST_SID}) 	
	for cookie in r.cookies:
		if cookie.name == "__Host-sid":
			API_HOST_SID = cookie.value			

	print_response(r.text)
	

# ---------
# put
# ---------
def put(endpoint, data):
	url = API_ENDPOINT + endpoint
	r = requests.put(url = url, json=data, verify=False, cookies={"__Host-sid": API_HOST_SID}) 
	print_response(r.text)


# ---------
# get
# ---------
def get(endpoint, data):
	print_request ("get", endpoint)
	url = API_ENDPOINT + endpoint
	# r = requests.get(url = url, json=data, verify=False, cookies={"__Host-sid": API_HOST_SID}) 
	r = requests.get(url = url, params=data, verify=False, cookies={"__Host-sid": API_HOST_SID}) 
	# print(r.url)
	print_response(r.text)
	return r.text
	# data = resp.json()
	
# ---------
# delete
# ---------
def delete(endpoint, data):
	url = API_ENDPOINT + endpoint
	r = requests.delete(url = url, json=data, verify=False, cookies={"__Host-sid": API_HOST_SID}) 
	output(r.text)

	
# ---------
# print_response
# ---------
def print_response(data):
	try:
		json_data = json.loads(data)
		pprint.pprint(json_data)
	except:
		print(data) 

# ---------
# print_request
# ---------
def print_request(method, endpoint):
	try:
		json_data = json.loads(data)
		pprint.pprint(bcolors.WARNING + endpoint + bcolors.ENDC)
	except:
		print("\n" + bcolors.BOLD + method + bcolors.ENDC + " " + bcolors.WARNING + endpoint + bcolors.ENDC)
		
# ---------
# sign_afip_cert
# ---------
def sign_afip_cert():

	print_request ("sign_afip_cert", " WSAA: http://localhost:9999")
    
	db = {}

	for proc in process_iter():
		for conns in proc.get_connections(kind='inet'):
			if conns.laddr[1] == 9999:
				proc.send_signal(SIGKILL) 
				continue

	with einvoice.start_services(db=db) as (wsaa, wsfe):

		with open("einvoice_csr.pem", 'r') as f:
			csr = f.read()

		cert = wsaa.sign_cert(csr=csr)

		with open('einvoice_test.crt', 'w') as f:
			f.write(cert)		

