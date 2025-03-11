# public
from spyne.decorator import srpc
from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.protocol.soap import Soap11  # , Soap12
from spyne.service import ServiceBase

# owner
from Auth import Auth
from FECAEAConsultar import *
from FECAEARegInformativo import *
from FECAEASinMovimientoConsultar import *
from FECAEASinMovimientoInformar import *
from FECAEASolicitar import *
from FECAESolicitar import *
from FECompConsultar import *
from FECompTotXRequest import *
from FECompUltimoAutorizado import *
from FEDummy import *
from FEParamGetTiposPaises import *
from FEParamGetTiposIva import *
from FEParamGetTiposTributos import *
from FEGetParamTypes import *

# ------------
# WSFE
# ------------
class WSFE(ServiceBase):

	__service_url_path__ = '/wsfev1/service.asmx'
	__tns__ = 'ar'
	__in_protocol__ = Soap11(validator='lxml')
	__out_protocol__ = Soap11()
	__name__ = "WSFE"
	
	# FECAEAConsultar
	@srpc(Auth, Integer, Integer, _returns=FECAEAConsultarResponse)
	def FECAEAConsultar(Auth, Periodo, Orden):
		return FECAEAConsultar().run()

	# FECAEARegInformativo
	@srpc(Auth, _returns=Unicode)
	def FECAEARegInformativo(Auth):		
		return 1		
	
	# FECAEASinMovimientoConsultar
	@srpc(Auth, Unicode, Integer, _returns=FECAEResponse)
	def FECAEASinMovimientoConsultar(Auth, CAEA, PtoVta):
		return FECAEASinMovimientoConsultar.run()		
	
	# FECAEASinMovimientoInformar
	@srpc(Auth, Unicode, Integer, _returns=FECAEResponse)
	def FECAEASinMovimientoInformar(Auth, CAEA, PtoVta):
		return FECAEASinMovimientoInformar.run()

	# FECAEASolicitar
	@srpc(Auth, Integer, Integer, _returns=FECAEASolicitarResponse)
	def FECAEASolicitar(Auth, Periodo, Orden):
		return FECAEASolicitar.run()
		
	# FECAESolicitar
	@srpc(Auth, FeCAEReq, _returns=FECAEResponse)
	def FECAESolicitar(Auth, FeCAEReq):
		return FECAESolicitar.run(FeCAEReq)		
		
	# FECompConsultar
	@srpc(Auth, FECompConsultarRequest, _returns=FECompConsultarResponse)
	def FECompConsultar(Auth, FeCompConsReq):
		return FECompConsultar().run()		
		
	# FECompTotXRequest
	@srpc(Auth, _returns=FERegXReqResponse)
	def FECompTotXRequest(Auth):
		return FERegXReqResponse(RegXReq=250)		
		
	# FECompUltimoAutorizado
	@srpc(Auth, Integer, Integer, _returns=FECompUltimoAutorizadoResponseXp)
	def FECompUltimoAutorizado(Auth, PtoVta, CbteTipo):
		return FECompUltimoAutorizado.run()
	
	# FEDummy
	@srpc(_returns=FEDummyResponse)
	def FEDummy():
		retval = FEDummyResponse()
		retval = {
			'AppServer' : 'OK', 
			'DbServer' : 'OK', 
			'AuthServer' : 'OK'
		}

		return retval	
	
	# FEParamGetCotizacion
	@srpc(Auth, _returns=Unicode)
	def FEParamGetCotizacion(Auth):		
		return 1

	# FEParamGetPtosVenta
	@srpc(Auth, _returns=Unicode)
	def FEParamGetPtosVenta(Auth):		
		return 1		

	# FEParamGetTiposCbte
	@srpc(Auth, _returns=Unicode)
	def FEParamGetTiposCbte(Auth):		
		return 1
		
	# FEParamGetTiposConcepto
	@srpc(Auth, _returns=Unicode)
	def FEParamGetTiposConcepto(Auth):		
		return 1

	# FEParamGetTiposDoc
	@srpc(Auth, _returns=Unicode)
	def FEParamGetTiposDoc(Auth):		
		return 1

	# FEParamGetTiposIva
	@srpc(Auth, _returns=IvaTipoResponse)
	def FEParamGetTiposIva(Auth):
		return FEParamGetTiposIva().run()		
		
	# FEParamGetTiposMonedas
	@srpc(Auth, _returns=Unicode)
	def FEParamGetTiposMonedas(Auth):		
		return 1
		
	# FEParamGetTiposOpcional
	@srpc(Auth, _returns=Unicode)
	def FEParamGetTiposOpcional(Auth):		
		return 1

	# FEParamGetTiposPaises
	@srpc(Auth, _returns=FEPaisResponse)
	def FEParamGetTiposPaises(Auth):
		return FEParamGetTiposPaises().run()
		
	# FEParamGetTiposTributos
	@srpc(Auth, _returns=FETributoResponse)
	def FEParamGetTiposTributos(Auth):
		obj = FEParamGetTiposTributos()
		return obj.run()		
		
	