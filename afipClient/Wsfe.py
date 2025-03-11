from Logger import *


# Wsfe
class Wsfe:

    # __init__
    def __init__(self):
        self._client = None
        self._auth = None
        self.logger = Logger()

    # setClient
    def setClient(self, client):
        self._client = client

    # setAuth
    def setAuth(self, auth):
        self._auth = auth
