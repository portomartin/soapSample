import sys
sys.path.insert(0, './classes')
sys.path.insert(0, './classes/types')
sys.path.insert(0, './classes/WSFE')
from WebServer import WebServer


if __name__ == "__main__":

	server = WebServer()
	server.port = 5002
	server.run()