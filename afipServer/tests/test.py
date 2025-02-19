from zeep import Client

c = Client('http://0.0.0.0:7789/?wsdl')
print(c.service.say_hello('punk', 5))

print(c.service.showPerson1({'name':'Ruben Miranda', 'age':22, 'nick':'Rubenza'}))
print(c.service.showPerson2({'name':'Ruben Miranda', 'age':22, 'nick':'Rubenza'}))
print(c.service.showPerson3({'name':'Ruben Miranda', 'age':22, 'nick':'Rubenza'}))
print(c.service.showPerson4({'name':'Ruben Miranda', 'age':22, 'nick':'Rubenza'}))
print(c.service.showPerson5({'name':'Ruben Miranda', 'age':22, 'nick':'Rubenza'}))
print(c.service.showPerson6({'name':'Ruben Miranda', 'age':22, 'nick':'Rubenza'}))

param = \
	{'Auth':
		{
			'Token':'000000', 
			'Sign': '111111', 
			'Cuit':'20 02020202'
		}, 
		'PtoVta' : 1, 
		'CbteTipo' : 1
	}

print(c.service.FECompUltimoAutorizado(param))
