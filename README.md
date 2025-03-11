# AFIP Client example
Time ago I needed to understand how the electronic invoice service of Argentina works (AFIP), in order to include it in an embedded POS system for ARM systems
So I put together a series of scripts that were scaling almost becoming an application. Reading the manuals of the agency and with this tool working I was able to understand the protocol I needed

# AFIP Server example
At the same time, built a mock service locally, in python, representing the same scheme of requests and responses, also using soap of course. I used this service to develop the AFIP Client tool more comfortably

# POS Client example
The POS system I mentioned is an embedded Point of Sale Server developed in C language. This system internally implements communication with AFIP. Therefore I needed this application to test the POS Server interface
