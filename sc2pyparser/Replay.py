from mpyq import MPQArchive
import StringIO

class Replay:

	DETAILS_TYPE_BIN		= '\x02'
	DETAILS_TYPE_ARRAY1		= '\x04'
	DETAILS_TYPE_ARRAY2		= '\x05'
	DETAILS_TYPE_TINYINT	= '\x06'
	DETAILS_TYPE_BIGINT		= '\x07'
	DETAILS_TYPE_VLF		= '\x09'

	FILE_NAME_DETAILS = 'replay.details'

	def __init__(self, filename):
	
		try:
			archive = MPQArchive(filename)
			files = archive.extract()
			
			for file_name, data in files.iteritems():
				if(file_name == self.FILE_NAME_DETAILS):
					self.parse_details(data)
			
		except IOError as (errno, strerror):
			print strerror
			
	def parse_details(self, data):
	
		i = 0
		while i < len(data):
			
			# \x02 binary data
			if(data[i] == self.DETAILS_TYPE_BIN):
				i = i+1
				length = ord(data[i])/2
				return data[i:i+length]
			
			# \x05 array
			if(data[i] == self.DETAILS_TYPE_ARRAY2):
				i = i+1
				length = ord(data[i])
				
				i = i+1
				# \x00 should follow length
				if data[i] != '\x00':
					raise Exception('This should have been \x00 in array')
					
				self.parse_details(data[i:])
				
			# \x04 array
			if(data[i] == self.DETAILS_TYPE_ARRAY1):
			
				# \x01 should follow identifyer...
				i = i+1
				if data[i] != '\x01':
					raise Exception('This should have been \x01 in array')

				# ... then \x00					
				i = i+1
				if data[i] != '\x00':
					raise Exception('This should have been \x00 in array')
					
				#l ... then length
				i = i+1
				length = ord(data[i])
				
				self.parse_details(data[i:])
			
			i = i + 1
			
#	def parse_number(self, data):
#		byteCount = 0;
#		value = 0;
#		byteCur;
#		
#		byteCur = src.get() & 0xFF
#		
#		while i < len(data):
#			while (data[i] & 0x80) != 0:
#				value = ((byteCur & 0x7F) << byteCount*7) | value
#				byteCount = byteCount + 1
#
#	                isNegative = (value & 0x01) != 0
#	                value = value >> 1;
#	                if isNegative:
#	                        value = -value
#	                
#	                return value;