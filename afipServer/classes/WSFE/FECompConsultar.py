from FECompConsultarTypes import *

# --------------
# FECompConsultar
# --------------
class FECompConsultar:
	
	def __init__(self):
		None

	# run
	def run(self):
	
		# arrayOfAlicIva
		data = ([5, 100, 21], [4, 50, 5.25])
		arr = [AlicIva(Id=v[0], BaseImp=v[1], Importe=v[2]) for v in data]
		arrayOfAlicIva = ArrayOfAlicIva(AlicIva=arr)		
		
		# arrayOfTributo
		tributo = Tributo(		
			Id = 99, 
			Desc = "Impuesto Municipal Matanza", 
			BaseImp = 150, 
			Alic = 5.2, 
			Importe = 7.8
		)
		
		arrayOfTributo = ArrayOfTributo(Tributo=[tributo])		
		
		# resultGet
		resultGet = ResultGet(			
			Concepto = 1, 
			DocTipo = 80, 
			DocNro = 20111111112, 
			CbteDesde = 1, 
			CbteHasta = 1, 
			CbteFch = 20100903, 
			ImpTotal = 184.05, 
			ImpTotConc = 0, 
			ImpNeto = 150, 
			ImpOpEx = 0, 
			ImpTrib = 7.8, 
			ImpIVA = 26.25, 
			FchServDesde = "", 
			FchServHasta = "", 
			FchVtoPago = "", 
			MonId = "PES", 
			MonCotiz = 1,
			
			Resultado = "A", 
			CodAutorizacion = 41124578989845, 
			EmisionTipo = "CAE", 
			FchVto = 20100913, 
			FchProceso = 20100902, 
			PtoVta = 12, 
			CbteTipo = 1, 
			
			Tributos = arrayOfTributo, 
			Iva = arrayOfAlicIva
		)
		
		errs = ArrayOfErr(Err=[])
		evts = ArrayOfEvt(Evt=[])
		resp = FECompConsultarResponse(ResultGet=resultGet, Errors=errs, Events=evts)
		return resp
		
