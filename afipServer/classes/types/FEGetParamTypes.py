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

# IvaTipo
class IvaTipo(ComplexModel):
    _type_info = [
        ('Id',  Unicode(min_occurs=1, max_occurs=1)),
        ('Desc', Unicode(min_occurs=0, max_occurs=1)),
        ('FchDesde', Unicode(min_occurs=0, max_occurs=1)),
        ('FchHasta', Unicode(min_occurs=0, max_occurs=1)),
    ]

class ArrayOfIvaTipo(ComplexModel):
    IvaTipo = IvaTipo.customize(min_occurs=0, max_occurs='unbounded', nillable=True)
	
class IvaTipoResponse(ComplexModel):
    _type_info = [
        ('ResultGet', ArrayOfIvaTipo),
        ('Errors', ArrayOfErr),
        ('Events', ArrayOfEvt),
    ]

# TributoTipo
class TributoTipo(ComplexModel):
    _type_info = [
        ('Id',  Short(min_occurs=1, max_occurs=1)),
        ('Desc', Unicode(min_occurs=0, max_occurs=1)),
        ('FchDesde', Unicode(min_occurs=0, max_occurs=1)),
        ('FchHasta', Unicode(min_occurs=0, max_occurs=1)),
    ]
	
class ArrayOfTributoTipo(ComplexModel):
    TributoTipo = TributoTipo.customize(min_occurs=0, max_occurs='unbounded', nillable=True)
	
class FETributoResponse(ComplexModel):
    _type_info = [
        ('ResultGet', ArrayOfTributoTipo),
        ('Errors', ArrayOfErr),
        ('Events', ArrayOfEvt),
    ]

# PaisTipo
class PaisTipo(ComplexModel):
    _type_info = [
        ('Id', Short(min_occurs=1, max_occurs=1)),
        ('Desc', Unicode(min_occurs=0, max_occurs=1)),
    ]	
	
class ArrayOfPaisTipo(ComplexModel):
    PaisTipo = PaisTipo.customize(min_occurs=0, max_occurs='unbounded', nillable=True)
	
class FEPaisResponse(ComplexModel):
    _type_info = [
        ('ResultGet', ArrayOfPaisTipo),
        ('Errors', ArrayOfErr),
        ('Events', ArrayOfEvt)
    ]	
	
class FERegXReqResponse(ComplexModel):
    _type_info = [
        ('RegXReq', Integer(min_occurs=1, max_occurs=1)),
        ('Errors', ArrayOfErr),
        ('Events', ArrayOfEvt)
    ]	