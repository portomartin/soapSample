from LoginCms import *
from FECompUltimoAutorizado import *
from FECAESolicitar import *
from FEDummy import *
from FECompConsultar import *
from FEParamGet import *
from Logger import *
from FECAEASolicitar import *
from FECAEAConsultar import *
from FECAEASinMovimientoInformar import *
from FECAEASinMovimientoConsultar import *


# AfipClient
class AfipClient:

    # __init__
    def __init__(self, type):

        self.wsa = None
        self.wsfe = None
        self.loginCms = None
        self.type = type

        self.logger = Logger()
        self.prepareService()

    # buildAuth
    def buildAuth(self):

        self.loginCms.getToken()

        auth = {
            "Token": self.loginCms.token,
            "Sign": self.loginCms.sign,
            "Cuit": self.loginCms.cuit,
        }

        # print (auth)
        return auth

    # prepareService
    def prepareService(self):

        # roots
        rootWsa = "https://wsaahomo.afip.gov.ar"
        rootWsfe = "https://wswhomo.afip.gov.ar"
        if self.type == "bsdu":
            rootWsa = "http://0.0.0.0:5002"
            rootWsfe = "http://0.0.0.0:5002"

        # wsa
        uriWsa = rootWsa + "/ws/services/LoginCms?wsdl"
        self.logger.info("Loading wsa from " + uriWsa)
        self.wsa = Client(uriWsa)

        # wsfe
        uriWsfe = rootWsfe + "/wsfev1/service.asmx?wsdl"
        self.logger.info("Loading wsfe from " + uriWsfe)
        self.wsfe = Client(uriWsfe)

        # setup wsa
        self.loginCms = LoginCms()
        self.loginCms.client = self.wsa

        # self.wsa = Client('https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl')
        # self.wsfe = Client('https://wswhomo.afip.gov.ar/wsfev1/service.asmx?wsdl')

    # processResponse
    def processResponse(self, response):

        self.logger.info(response)

        try:
            if response.Errors.Err[0].Code == 600:
                self.loginCms.getNewToken()

        except:
            None

    # FECompUltimoAutorizado
    def fECompUltimoAutorizado(self):
        self.processResponse(self.buildObject("FECompUltimoAutorizado").run())

    # FECAESolicitar
    def fECAESolicitar(self):
        self.processResponse(self.buildObject("FECAESolicitar").run())

    # FECompConsultar
    def fECompConsultar(self):
        self.processResponse(self.buildObject("FECompConsultar").run())

    # FECAEASolicitar
    def fECAEASolicitar(self):
        self.processResponse(self.buildObject("FECAEASolicitar").run())

    # fECAEAConsultar
    def fECAEAConsultar(self):
        self.processResponse(self.buildObject("FECAEAConsultar").run())

    # FECAEASinMovimientoInformar
    def fECAEASinMovimientoInformar(self):
        self.processResponse(self.buildObject("FECAEASinMovimientoInformar").run())

    # FECAEASinMovimientoConsultar
    def fECAEASinMovimientoConsultar(self):
        self.processResponse(self.buildObject("FECAEASinMovimientoConsultar").run())

    # buildObject
    def buildObject(self, className):
        module = __import__(className)
        class_ = getattr(module, className)
        obj = class_()
        obj.setAuth(self.buildAuth())
        obj.setClient(self.wsfe)
        return obj

    # FEParamGet
    def fEParamGet(self, param):
        self.processResponse(self.buildObject("FEParamGet").run(param))

    # FEDummy
    def fEDummy(self):
        self.processResponse(self.buildObject("FEDummy").run())
