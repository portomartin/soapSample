from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.model.complex import Iterable, ComplexModel  # Array


class Evt(ComplexModel):
    _type_info = [
        ('Code', Integer(min_occurs=1, max_occurs=1)),
        ('Msg', Unicode(min_occurs=0, max_occurs=1)),
    ]


class ArrayOfEvt(ComplexModel):
    Evt = Evt.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

class Err(ComplexModel):
    _type_info = [
        ('Code', Integer(min_occurs=1, max_occurs=1)),
        ('Msg', Unicode(min_occurs=0, max_occurs=1)),
    ]
	
class ArrayOfErr(ComplexModel):
    Err = Err.customize(min_occurs=0, max_occurs='unbounded', nillable=True)


class Tributo(ComplexModel):
    _type_info = [
        ('Id', Integer(min_occurs=1, max_occurs=1)),
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
	
class ArrayOfTributo(ComplexModel):
    Tributo = Tributo.customize(min_occurs=0, max_occurs='unbounded', nillable=True)

class ArrayOfAlicIva(ComplexModel):
    AlicIva = AlicIva.customize(min_occurs=0, max_occurs='unbounded', nillable=True)
	
class ResultGet(ComplexModel):
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
        
        ('Tributos', ArrayOfTributo),
        ('Iva', ArrayOfAlicIva),
		
		('Resultado', Unicode(min_occurs=1, max_occurs=1)),
		('CodAutorizacion', Unicode(min_occurs=1, max_occurs=1)),
		('EmisionTipo', Unicode(min_occurs=1, max_occurs=1)),
		('FchVto', Unicode(min_occurs=1, max_occurs=1)),
		('FchProceso', Unicode(min_occurs=1, max_occurs=1)),
		('PtoVta', Integer(min_occurs=1, max_occurs=1)),
		('CbteTipo', Integer(min_occurs=1, max_occurs=1))
    ]
	
class FECompConsultarResponse(ComplexModel):
    _type_info = [
        ('ResultGet', ResultGet),
        ('Errors', ArrayOfErr),
        ('Events', ArrayOfEvt)
    ]	
	
class FECompConsultarRequest(ComplexModel):
    _type_info = [
        ('CbteTipo', Integer(min_occurs=1, max_occurs=1)),
        ('CbteNro', Long(min_occurs=1, max_occurs=1)),
        ('PtoVta', Integer(min_occurs=1, max_occurs=1))
    ]	