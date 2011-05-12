from sc2replaylib.parsers import Parser, ParserException

class DetailsParser(Parser):

	DETAILS_TYPE_BIN			= '\x02'
	DETAILS_TYPE_ARRAY			= '\x04'
	DETAILS_TYPE_INDEXED_ARRAY	= '\x05'
	DETAILS_TYPE_TINYINT		= '\x06'
	DETAILS_TYPE_BIGINT			= '\x07'
	DETAILS_TYPE_VLF			= '\x09'
		
	def __init__(self, raw_data):
		self.raw_data		= raw_data
		self.parsed_data	= None
	
	def parse(self):
		if self.parsed_data == None:
			(self.parsed_data, length) = self.parse_details(self.raw_data)
			
		return self.parsed_data
	
	# Recursive function to parse_details
	def parse_details(self, data):
		i = 0
		
		# \x02 binary data
		if(data[i] == self.DETAILS_TYPE_BIN):		
			i += 1
			
			(length, movement) = self.parse_number(data[i:])
			i += movement + 1
						
			return (data[i : i + length], i + length)
			
		# \x04 array
		elif(data[i] == self.DETAILS_TYPE_ARRAY):
		
			# \x01 should follow identifyer...
			i += 1
			if data[i] != '\x01':
				raise ParserException('This should have been \x01 in array')

			# ... then \x00					
			i += 1
			if data[i] != '\x00':
				raise ParserException('This should have been \x00 in array')
				
			# ... then length
			i += 1
			(length, movement) = self.parse_number(data[i:])
			i += movement + 1
			
			# move up i to the data!
			j = 0
			return_array = []
			
			while j < length:
								
				(new_data, movement) = self.parse_details(data[i:])				
				i += movement
				
				return_array.append(new_data)
				
				j += 1
							
			return (return_array, i)
					
		# \x05 Indexed array
		elif(data[i] == self.DETAILS_TYPE_INDEXED_ARRAY):
			i += 1
			
			(length, movement) = self.parse_number(data[i:])
			i += movement + 1
			
			return_array = []
			nulls = 0
			curr_idx = 0
			
			while (curr_idx - nulls) < length:

				# get index and check for 'null' entries - THEY DO NOT COUNT AGAINST ARRAY LENGTH
				(idx, movement) = self.parse_number(data[i:])
				i += movement + 1
				
				while idx > (curr_idx):
					return_array.append(None)
					curr_idx += 1
					nulls += 1
					
				curr_idx = idx
				(new_data, movement) = self.parse_details(data[i:])				
				i += movement
				
				return_array.append(new_data)				
				curr_idx += 1

			return (return_array, i)
		
		elif(data[i] == self.DETAILS_TYPE_TINYINT):
			i += 1			
			return (ord(data[i]), i + 1)
		
		#\x07 Big Integer
		elif(data[i] == self.DETAILS_TYPE_BIGINT):
			i += 1
			
			hex_str = hex(ord(data[i])) + str(hex(ord(data[i+1]))[2:]) + str(hex(ord(data[i+2]))[2:]) + str(hex(ord(data[i+3]))[2:])
			
			return (int(hex_str, 16), i+4)
		
		# \x09 VLF number found
		elif(data[i] == self.DETAILS_TYPE_VLF):
			i += 1
						
			(value, movement) = self.parse_number(data[i:])
			return (value, i + movement+1)
			
	def parse_number(self, data):
		i = 0

		# is the next byte going to be influential on this number?
		while ord(data[i]) & 0x80 == 0x80:
			i += 1

		value = ord(data[i]) & 0x7F
		
		j = i-1
		while j >= 0:
			bit = ord(data[j]) & 0x7F
			value = value << 7
			value = value | bit
			j -= 1
		
		if value & 1 == 1:
			value = (value >> 1) * -1
		else:
			value = (value >> 1)
		
		return (value, i)
