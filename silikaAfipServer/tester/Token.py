from collections import namedtuple

class Token:

	# __init__
	def __init__(self):
		Token = namedtuple('Token', 'token, sign, expiration, id')
	
		self.token = Token(token='PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+CiAgICA8aWQgc3JjPSJDTj13c2FhaG9tbywgTz1BRklQLCBDPUFSLCBTRVJJQUxOVU1CRVI9Q1VJVCAzMzY5MzQ1MDIzOSIgZHN0PSJDTj13c2ZlLCBPPUFGSVAsIEM9QVIiIHVuaXF1ZV9pZD0iMTc3MzE0NDAwNSIgZ2VuX3RpbWU9IjE2Mjk3NTg0NDAiIGV4cF90aW1lPSIxNjI5ODAxNzAwIi8+CiAgICA8b3BlcmF0aW9uIHR5cGU9ImxvZ2luIiB2YWx1ZT0iZ3JhbnRlZCI+CiAgICAgICAgPGxvZ2luIGVudGl0eT0iMzM2OTM0NTAyMzkiIHNlcnZpY2U9IndzZmUiIHVpZD0iU0VSSUFMTlVNQkVSPUNVSVQgMjAzODE1MTAxMTYsIENOPWVpbnZvaWNlIiBhdXRobWV0aG9kPSJjbXMiIHJlZ21ldGhvZD0iMjIiPgogICAgICAgICAgICA8cmVsYXRpb25zPgogICAgICAgICAgICAgICAgPHJlbGF0aW9uIGtleT0iMjAzODE1MTAxMTYiIHJlbHR5cGU9IjQiLz4KICAgICAgICAgICAgPC9yZWxhdGlvbnM+CiAgICAgICAgPC9sb2dpbj4KICAgIDwvb3BlcmF0aW9uPgo8L3Nzbz4K', sign='e/IY9jeJfPqzTnbDHUdw5Xa3nKbfVKsrblP4/nYNDLZCRdZJ/hZRH3F/Bmfmq8wE1RV5ZD3c4fViwYWylTUum3G6Q08cZdr3+HCsb6xte2/8edLKTJ7C8Sm0ZltuIKaHNuPK+4oMmI1gAQFxPFCltKf9YaJ1GBYJ6MzpnZJodJg=', expiration='2021-08-24T07:41:40.952-03:00', id='20381510116')
		# token = get_token(args.cert, args.private_key, duration=30)
		# always print the token because we need to reuse it due to AFIP's server cooldown
		# print token
		# print ("init")

		
	