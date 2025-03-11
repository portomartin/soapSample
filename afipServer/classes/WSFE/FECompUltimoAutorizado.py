from spyne.model.complex import ComplexModel
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode
from Auth import *

# class Auth(ComplexModel):
		# Token = Unicode
		# Sign = Unicode
		# Cuit = Unicode
		
# FECompUltimoAutorizadoRequest
class FECompUltimoAutorizadoRequest(ComplexModel):
	
	# class AuthRequest(ComplexModel):
		# Token = Unicode
		# Sign = Unicode
		# Cuit = Unicode
	
	Auth = Auth
	PtoVta = Integer
	CbteTipo = Integer
	
# FECompUltimoAutorizadoResponseXp
class FECompUltimoAutorizadoResponseXp(ComplexModel):
	
	PtoVta = Integer
	CbteTipo = Integer
	CbteNro = Integer


# FECompUltimoAutorizado
class FECompUltimoAutorizado:
	
	def __init__(self):
		None

	# run
	def run(self):	
		ret = FECompUltimoAutorizadoResponseXp()
		ret.PtoVta = 1
		ret.CbteTipo = 1
		ret.CbteNro = 2
		return ret

