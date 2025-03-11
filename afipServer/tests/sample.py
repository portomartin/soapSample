import datetime


import logging

from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.model.complex import ComplexModel
from spyne.model.complex import Iterable
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode

from spyne.util.simple import wsgi_soap_application

from FECompUltimoAutorizado import *


class SomeObject(ComplexModel):
	__namespace__ = 'aaa'

	i = Integer
	s = Unicode


# Person
class Person(ComplexModel):
	name = Unicode
	age = Integer
	nick = Unicode
	

# Friend
class Friend(ComplexModel):
	__namespace__ = "ar"	
	
	name = Unicode
	born = Integer


# BestFriend
class BestFriend(ComplexModel):	
	friend = Friend

	

# showPerson
def showPerson(person):
	
	friend = Friend()		
	friend.name = person.nick		
	now = datetime.datetime.now()
	friend.born = now.year - person.age		
	return friend		
	

# HelloWorldService
class HelloWorldService(ServiceBase):


	# __out_header__ = SomeObject
	@srpc(Unicode, Integer, _returns=Iterable(Unicode))
	def say_hello(name, times):
		for i in range(times):
			yield u'Hello, %s' % name
			

	# showPerson1
	@srpc(Person, _returns=Unicode)
	def showPerson1(person):
		return u'Name:%s Age:%d Nick:%s' % (person.name, person.age, person.nick)
		

	# showPerson2
	@srpc(Person, _returns=Integer)
	def showPerson2(person):
		return person.age
		

	# showPerson3
	@srpc(Person, _returns=Iterable(Integer))
	def showPerson3(person):
		aux = []
		for i in range(3):
			aux.append(person.age)
		
		return aux

	
	# showPerson4
	@srpc(Person, _returns=Friend)
	def showPerson4(person):		
		return showPerson(person)

	
	# showPerson5
	@srpc(Person, _returns=BestFriend)
	def showPerson5(person):
		
		friend = Friend()		
		friend.name = person.nick		
		now = datetime.datetime.now()
		friend.born = now.year - person.age
		
		bestFriend = BestFriend()
		bestFriend.friend = friend
		
		return bestFriend


	# showPerson6
	@srpc(Person, _returns=BestFriend)
	def showPerson6(person):
		
		friend = showPerson(person)
		bestFriend = BestFriend()
		bestFriend.friend = friend
		
		return bestFriend
		
		
	# showPerson6
	@srpc(Auth, Integer, Integer, _returns=FECompUltimoAutorizadoResponseXp)
	def FECompUltimoAutorizado(Auth, PtoVta, CbteTipo):
		
		ret = FECompUltimoAutorizadoResponseXp()
		obj = FECompUltimoAutorizado()
		return obj.run()
		
		
def on_method_return_string(ctx):
	print "---------------------"
	print ctx.out_string[0]
	ctx.out_string[0] = "caca"
	return ctx.out_string[0]


if __name__=='__main__':

	from wsgiref.simple_server import make_server

	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

	logging.info("listening to http://0.0.0.0:7789")
	logging.info("wsdl is at: http://localhost:7789/?wsdl")

	HelloWorldService.event_manager.add_listener('method_return_string', on_method_return_string)
	wsgi_app = wsgi_soap_application([HelloWorldService], 'spyne.examples.hello.soap')
	
	server = make_server('0.0.0.0', 7789, wsgi_app)
	server.serve_forever()
	
	
	