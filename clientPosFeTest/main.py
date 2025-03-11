from einvoice_api import *
from sales_api import *
	
# basic setup
login()
config_datetime()

# store setup
config_business()
config_get_business()
config_business_extra_info()
config_get_business_extra_info()

# einvoice setup 
config_einvoice()
config_get_einvoice()
einvoice_csr()
# sign_afip_cert()
# cert_remove()
cert_load()

# einvoice status
einvoice_enable()
einvoice_get_status()
einvoice_get_server_status()
einvoice_check_service_access()

# sales
cancela_venta_en_curso()
agrega_item_polo_bolsillo()
display()
sale_close()

