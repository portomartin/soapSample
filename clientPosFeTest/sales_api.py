from api import *

# ----------------------------
# login
# ----------------------------
def login():   
	post("/auth/login", {"user": "admin", "password": "1234567890"})

# ----------------------------
# cancela_venta_en_curso
# ----------------------------
def cancela_venta_en_curso():   
	post("/sale/cancel", {})


# ----------------------------
# promo_reset
# ----------------------------
def promo_reset():   

	delete("/promo/rule_condition/", {"id": "1"})
	delete("/promo/order/rule_condition/", {"id": "10"})
	delete("/promo/rule/", {"id": "1"})
	delete("/promo/rule/", {"id": "2"})


# ----------------------------
# display
# ----------------------------
def display():   

	get("/promo/order/rule/download", {})
	get("/promo/order/rule_condition/download", {})	
	get("/sale/cart", {})	

	
# ----------------------------
# agrega_item_polo_bolsillo
# ----------------------------
def agrega_item_polo_bolsillo():   

	data = {
	  "product_id": "1000000000016",
	  "quantity": "1.000"
	}
	post("/sale/item", data)   


# ----------------------------
# agrega_item_polo_basic
# ----------------------------
def agrega_item_polo_basic(): 

	data = {
	  "product_id": "1000000000023",
	  "quantity": "1.000"
	}
	post("/sale/item", data)   
	
# sale_close()
def sale_close():
	post("/sale/close", {})

