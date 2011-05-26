import struct

from sc2replaylib.parsers import Parser, ParserException

class AttributesParser(Parser):
				
	ATTRIB_BYTE_SIZ		= 13
	ATTRIB_HEADER_OFFSET	= 9
		
	def __init__(self, raw_data):
		self.raw_data = raw_data
		self.parsed_data = None
			
	def parse(self):
		if self.parsed_data == None:
		 	self.parsed_data = self.parse_events(self.raw_data)
			
		return self.parsed_data
		
		
	def unpack_int32(self, data):
		return struct.unpack_from('<I', data)[0]
		
	def unpack_str(self, data):
		return struct.unpack_from('4s',data)[0][::-1].replace('\x00','')
		
	# parses an attribute packet
	def parse_attribute(self, data):
		try:
			return tuple([
				self.unpack_int32(data[0:4]),
				self.unpack_int32(data[4:8]),
				ord(data[8:9]),
				self.unpack_str(data[9:13])])
		except Exception, err:
			raise ParserException('Could not parse attribute: %s' % err)
		
	def parse_events(self, data):

		# attributes header, 9 bytes long
		# should look like: 00  00  00  00  00  aa  aa  aa  aa
		#                   ^ 5 bytes of zeros  ^ 4 byte int of total attribute length			
		self.length = self.unpack_int32(data[5:9])
			
		# parse 13 byte blocks until self.length is met
		i = 0
		parsed = []
		while i < self.length:
			parsed.append(self.parse_attribute(data[
				self.ATTRIB_HEADER_OFFSET+(self.ATTRIB_BYTE_SIZE*i):
				self.ATTRIB_HEADER_OFFSET+(self.ATTRIB_BYTE_SIZE*(i+1))]))
			i += 1
			
		return tuple(parsed)
