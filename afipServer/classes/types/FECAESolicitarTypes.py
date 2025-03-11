from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.model.complex import Iterable, ComplexModel  # Array
from Auth import *

# Evt
class Evt(ComplexModel):
    _type_info = [
        ('Code', Integer(min_occurs=1, max_occurs=1)),
        ('Msg', Unicode(min_occurs=0, max_occurs=1)),
    ]

# ArrayOfEvt
class ArrayOfEvt(ComplexModel):
    Evt = Evt.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

# Err
class Err(ComplexModel):
    _type_info = [
        ('Code', Integer(min_occurs=1, max_occurs=1)),
        ('Msg', Unicode(min_occurs=0, max_occurs=1)),
    ]

# ArrayOfErr
class ArrayOfErr(ComplexModel):
    Err = Err.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

# Obs
class Obs(ComplexModel):
    _type_info = [
        ('Code', Integer(min_occurs=1, max_occurs=1)),
        ('Msg', Unicode(min_occurs=0, max_occurs=1)),
    ]

# ArrayOfObs
class ArrayOfObs(ComplexModel):
    Obs = Obs.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

# FEDetResponse
class FEDetResponse(ComplexModel):
    _type_info = [
        ('Concepto', Integer(min_occurs=1, max_occurs=1)),
        ('DocTipo', Integer(min_occurs=1, max_occurs=1)),
        ('DocNro', Long(min_occurs=1, max_occurs=1)),
        ('CbteDesde', Long(min_occurs=1, max_occurs=1)),
        ('CbteHasta', Long(min_occurs=1, max_occurs=1)),
        ('CbteFch', Unicode(min_occurs=0, max_occurs=1)),
        ('Resultado', Unicode(min_occurs=0, max_occurs=1)),
        ('Observaciones', ArrayOfObs)
    ]

# FECAEDetResponse
class FECAEDetResponse(FEDetResponse):
    CAE = Unicode(min_occurs=0, max_occurs=1)
    CAEFchVto = Unicode(min_occurs=0, max_occurs=1)

# FeCabResp
class FeCabResp(ComplexModel):
    _type_info = [
        ('Cuit', Long(min_occurs=1, max_occurs=1)),
        ('PtoVta', Integer(min_occurs=1, max_occurs=1)),
        ('CbteTipo', Integer(min_occurs=1, max_occurs=1)),
        ('FchProceso', Unicode(min_occurs=0, max_occurs=1)),
        ('CantReg', Integer(min_occurs=1, max_occurs=1)),
        ('Resultado', Unicode(min_occurs=0, max_occurs=1)),
        ('Reproceso', Unicode(min_occurs=0, max_occurs=1)),
    ]

# FECAEResponse
class FECAEResponse(ComplexModel):
    _type_info = [
        ('FeCabResp', FeCabResp),
        ('FeDetResp', FECAEDetResponse.customize(min_occurs=0, max_occurs='unbounded', nillable=True)),
        ('Errors', ArrayOfErr),
        ('Events', ArrayOfEvt),
    ]
	
	
# requests types
class CbteAsoc(ComplexModel):
    _type_info = [
        ('Tipo', Integer(min_occurs=1, max_occurs=1)),
        ('PtoVta', Integer(min_occurs=1, max_occurs=1)),
        ('Nro', Long(min_occurs=1, max_occurs=1)),
    ]

class Tributo(ComplexModel):
    _type_info = [
        ('Id', Short(min_occurs=1, max_occurs=1)),
        ('Desc', Unicode(min_occurs=0, max_occurs=1)),
        ('BaseImp', Double(min_occurs=1, max_occurs=1)),
        ('Alic', Double(min_occurs=1, max_occurs=1)),
        ('Importe', Double(min_occurs=1, max_occurs=1)),
    ]
	
class AlicIva(ComplexModel):
    _type_info = [
        ('Id', Integer(min_occurs=1, max_occurs=1)),
        ('BaseImp', Double(min_occurs=1, max_occurs=1)),
        ('Importe', Double(min_occurs=1, max_occurs=1)),
    ]
	
class Opcional(ComplexModel):
    _type_info = [
        ('Id', Unicode(min_occurs=0, max_occurs=1)),
        ('Valor', Unicode(min_occurs=0, max_occurs=1)),
    ]
	
class ArrayOfCbteAsoc(ComplexModel):
    CbteAsoc = CbteAsoc.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

class ArrayOfOpcional(ComplexModel):
    Opcional = Opcional.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

class ArrayOfTributo(ComplexModel):
    Tributo = Tributo.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

class ArrayOfAlicIva(ComplexModel):
    AlicIva = AlicIva.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

class FEDetRequest(ComplexModel):
    _type_info = [
        ('Concepto', Integer(min_occurs=1, max_occurs=1)),
        ('DocTipo', Integer(min_occurs=1, max_occurs=1)),
        ('DocNro', Long(min_occurs=1, max_occurs=1)),
        ('CbteDesde', Long(min_occurs=1, max_occurs=1)),
        ('CbteHasta', Long(min_occurs=1, max_occurs=1)),
        ('CbteFch', Unicode(min_occurs=0, max_occurs=1)),
        ('ImpTotal', Double(min_occurs=1, max_occurs=1)),
        ('ImpTotConc', Double(min_occurs=1, max_occurs=1)),
        ('ImpNeto', Double(min_occurs=1, max_occurs=1)),
        ('ImpOpEx', Double(min_occurs=1, max_occurs=1)),
        ('ImpTrib', Double(min_occurs=1, max_occurs=1)),
        ('ImpIVA', Double(min_occurs=1, max_occurs=1)),
        ('FchServDesde', Unicode(min_occurs=0, max_occurs=1)),
        ('FchServHasta', Unicode(min_occurs=0, max_occurs=1)),
        ('FchVtoPago', Unicode(min_occurs=0, max_occurs=1)),
        ('MonId', Unicode(min_occurs=0, max_occurs=1)),
        ('MonCotiz', Double(min_occurs=1, max_occurs=1)),
        ('CbtesAsoc', ArrayOfCbteAsoc),
        ('Tributos', ArrayOfTributo),
        ('Iva', ArrayOfAlicIva),
        ('Opcionales', ArrayOfOpcional),
    ]


class FECAEDetRequest(FEDetRequest):
    pass

class FECAECabRequest(ComplexModel):
    _type_info = [
        ('CantReg', Integer(min_occurs=1, max_occurs=1),),
        ('PtoVta', Integer(min_occurs=1, max_occurs=1),),
        ('CbteTipo', Integer(min_occurs=1, max_occurs=1),),
    ]

class FeCAEReq(ComplexModel):
    _type_info = [
        ('FeCabReq', FECAECabRequest),
        ('FeDetReq', FECAEDetRequest.customize(min_occurs=0, max_occurs='unbounded', nillable=True))
    ]	