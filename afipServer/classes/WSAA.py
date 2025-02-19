# public
from spyne.decorator import srpc
from spyne.model.primitive import Unicode, Integer, Double, Long, Short
from spyne.protocol.soap import Soap11  # , Soap12
from spyne.service import ServiceBase

# owner

# ------------
# WSAA
# ------------
class WSAA(ServiceBase):

	__service_url_path__ = '/ws/services/LoginCms'
	__tns__ = 'ar'
	__in_protocol__ = Soap11(validator='lxml')
	__out_protocol__ = Soap11()
	__name__ = "WSAA"

	@srpc(Unicode, _returns=Unicode, _out_variable_name="loginCmsReturn")
	def loginCms(in0):
		out = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
			<loginTicketResponse version="1">
				<header>
					<source>CN=wsaahomo, O=AFIP, C=AR, SERIALNUMBER=CUIT 33693450239</source>
					<destination>CN=papa, SERIALNUMBER=CUIT 20935268037, O=guglielmone nemi alex, C=ar</destination>
					<uniqueId>577238412</uniqueId>
					<generationTime>2016-11-08T11:27:18.792-03:00</generationTime>
					<expirationTime>2016-11-08T23:27:18.792-03:00</expirationTime>
				</header>
				<credentials>
					<token>PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+CiAgICA8aWQgdW5pcXVlX2lkPSIxMDExMzI4NTkzIiBzcmM9IkNOPXdzYWFob21vLCBPPUFGSVAsIEM9QVIsIFNFUklBTE5VTUJFUj1DVUlUIDMzNjkzNDUwMjM5IiBnZW5fdGltZT0iMTQ3ODYxNTE3OCIgZXhwX3RpbWU9IjE0Nzg2NTg0MzgiIGRzdD0iQ049d3NmZSwgTz1BRklQLCBDPUFSIi8+CiAgICA8b3BlcmF0aW9uIHZhbHVlPSJncmFudGVkIiB0eXBlPSJsb2dpbiI+CiAgICAgICAgPGxvZ2luIHVpZD0iQ049cGFwYSwgU0VSSUFMTlVNQkVSPUNVSVQgMjA5MzUyNjgwMzcsIE89Z3VnbGllbG1vbmUgbmVtaSBhbGV4LCBDPWFyIiBzZXJ2aWNlPSJ3c2ZlIiByZWdtZXRob2Q9IjIyIiBlbnRpdHk9IjMzNjkzNDUwMjM5IiBhdXRobWV0aG9kPSJjbXMiPgogICAgICAgICAgICA8cmVsYXRpb25zPgogICAgICAgICAgICAgICAgPHJlbGF0aW9uIHJlbHR5cGU9IjQiIGtleT0iMjA5MzUyNjgwMzciLz4KICAgICAgICAgICAgPC9yZWxhdGlvbnM+CiAgICAgICAgPC9sb2dpbj4KICAgIDwvb3BlcmF0aW9uPgo8L3Nzbz4KCg==</token>
					<sign>YGHsu2ARIxZUskoQhyqH0tWDOiDffWLjH6Hj5sg3zIcr+MODgpXfwjN0C+1zxgBIZ3YE1oOX2+OVcMAWs1tqboYm50/+zoHFS91bRM5ngOOpDXZX0IGFjf4eTwNw3KdB9fhAKDLP3Cv7wElw09YYuYcFn1+jJh4951ZsPhWInow=</sign>
				</credentials>
			</loginTicketResponse>'''
		return out
	
	