from api import *
import base64

# login()
def login():
	post("/auth/login", 
		{
			"user": "admin", 
			"password": "1234"
		}
	)

# config_datetime
def config_datetime():   
	post("/config/datetime", 
		{
			"datetime": "2021-08-31T15:22:15-03:00"
		}		
	)
	
# config_get_einvoice
def config_get_einvoice():   
	get("/config/einvoice", {})   	
	
# config_einvoice
def config_einvoice():   
	post("/config/einvoice", 
		{
			"wsaa_url": "http://localhost:9999",
			"wsfe_url": "http://localhost:10000",
			"pos": 1,
			"offline_pos": 1
		}
	)	
   
# einvoice_check_service_access
def einvoice_check_service_access():   
	get("/einvoice/service/access", {})	
   
# config_business
def config_business():   
	post("/config/business", 
		{
		  "gross_income_id": "1",
		  "vat_responsibility": "vat_responsibility_responsible",
		  "receipt_invoice_a_type": "receipt_invoice_a_type_normal",
		  "tributary_id": "20352146170"
		}
	)
   
# config_get_business
def config_get_business():   
	get("/config/business", {})	
	
# config_get_business_extra_info
def config_get_business_extra_info():
	get("/config/business/extra/info", {})
	
# config_business_extra_info()
def config_business_extra_info():
	post("/config/business/extra/info", 
		{
		  "fantasy_name": "El Boli",
		  "name": "El Boli"
		}
	)
	
# einvoice_csr
def einvoice_csr():
	response = get("/einvoice/cert/csr", 
		{
		"fields":
			'{"key_slot": 1, "format": "cert_format_pem"}'
		}
	)
	
	response_data = json.loads(response)

	f = open('einvoice_csr.pem', 'w' )
	f.write(base64.b64decode(response_data.get('csr_data')))
	f.close()

# sign_afip_cert
def sign_afip_cert():
	sign_afip_cert()

	
# cert_load
def cert_load():

	with open('einvoice_test.crt', 'r') as file:
		data = file.read()		
		
		post("/crypto/cert/load", 
			{
			  "data": base64.b64encode(data),
			  "format": "cert_format_pem",
			  "tags": [
				"certs_tag_afip"
			  ]
			}
		)
	
# cert_remove
def cert_remove():

	post("/crypto/cert/remove", 
		{
		  "tag": "certs_tag_afip"
		}
	)

# einvoice_check_service_access
def einvoice_check_service_access():
	get("/einvoice/service/access", {})

# einvoice_get_status
def einvoice_get_status():
	get("/einvoice/status", {})

# einvoice_get_server_status
def einvoice_get_server_status():
	get("/einvoice/server/status", {})

# einvoice_enable
def einvoice_enable():

	post("/einvoice/enable", 
		{
			"enable": True
		}
	)
