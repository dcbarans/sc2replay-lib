from abc import ABCMeta, abstractmethod

from sc2replaylib import Sc2replaylibException

class Parser:
	__metaclass__ = ABCMeta
	
	@abstractmethod
	def parse(self):
		pass

class ParserException(Sc2replaylibException):
	pass