import struct
from pprint import pprint

from sc2replaylib.parsers import Parser, ParserException

class AttributesParser(Parser):
		
		events_data = None
		
		ATTRIB_BYTE_SIZE		= 13
		ATTRIB_HEADER_OFFSET	= 9
		
		def __init__(self, events_data):
			self.events_data = events_data
			
		def parse(self):
			return self.parse_events(self.events_data)
		
		
		def parse_int32(self, data):
			return struct.unpack_from('<I', data)[0]
		
		# parses an attribute packet
		def parse_attribute(self, data):
			
			
			pprint(data)
		
		def parse_events(self, data):
			#pprint(data)
			
			# attributes header, 9 bytes long
			# should look like: 00  00  00  00  00  aa  aa  aa  aa
			#                   ^ 5 bytes of zeros  ^ 4 byte int of total attribute length
			
			self.length = self.parse_int32(data[5:9])

			print self.length
			
			pprint(data[9:13])
			print self.parse_int32(data[9:13])
			print "\n\n\n"
			
			# parse 13 byte blocks until there are no more
			i = 0
			while i < self.length:
				self.parse_attribute(data[
					self.ATTRIB_HEADER_OFFSET+(self.ATTRIB_BYTE_SIZE*i):
					self.ATTRIB_HEADER_OFFSET+(self.ATTRIB_BYTE_SIZE*(i+1))])
				i += 1
				break
			
			#pprint(data[9:10])
			#print ord(data[9])
			
			