from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.model.complex import Iterable, ComplexModel  # Array

class Auth(ComplexModel):

    _type_info = [
        ('Token', Unicode(min_occurs=0, max_occurs=1)),
        ('Sign', Unicode(min_occurs=0, max_occurs=1)),
        ('Cuit', Unicode(min_occurs=1, max_occurs=1)),
    ]
	