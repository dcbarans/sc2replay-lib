from mpyq import MPQArchive
import StringIO

from pprint import pprint

DEBUG = True

class Replay:

	DETAILS_TYPE_BIN			= '\x02'
	DETAILS_TYPE_ARRAY			= '\x04'
	DETAILS_TYPE_INDEXED_ARRAY	= '\x05'
	DETAILS_TYPE_TINYINT		= '\x06'
	DETAILS_TYPE_BIGINT			= '\x07'
	DETAILS_TYPE_VLF			= '\x09'

	FILE_NAME_DETAILS = 'replay.details'
		
	def __init__(self, filename):
		
		try:
			archive = MPQArchive(filename)
			files = archive.extract()
			
			for file_name, data in files.iteritems():
				if(file_name == self.FILE_NAME_DETAILS):
					(parsed_data, length) = self.parse_details(data)
			
		except IOError as (errno, strerror):
			print strerror
	
	'''
	Recursive function to parse_details
	'''
	def parse_details(self, data):
	
		i = 0
	
		if DEBUG:
			pprint(data[i])
	
		# \x02 binary data
		if(data[i] == self.DETAILS_TYPE_BIN):
		
			print 'found bin'
		
			i += 1
			(length, movement) = self.parse_number(data[i:])
			i += movement + 1
			
			if DEBUG:
				print "Bin: len(" + str(length) + ") = " + data[i : i + length]
			
			return (data[i : i + length], i + length)
			
		# \x04 array
		elif(data[i] == self.DETAILS_TYPE_ARRAY):
		
			print 'found array'
		
			# \x01 should follow identifyer...
			i += 1
			if data[i] != '\x01':
				raise Exception('This should have been \x01 in array')

			# ... then \x00					
			i += 1
			if data[i] != '\x00':
				raise Exception('This should have been \x00 in array')
				
			# ... then length
			i += 1
			(length, movement) = self.parse_number(data[i:])
			i += movement
			
			if DEBUG:
				print "Array: len(" + str(length) + ")"
			
			# move up i to the data!
			i += 1
			j = 0
			return_array = []
			
			while j < length:
				
				print 'array looping: ' + str(j) + " < " + str(length)
				
				
				(new_data, movement) = self.parse_details(data[i:])
				
				i += movement
				return_array.append(new_data)
				
				
				if DEBUG:
					print "returned: " + return_array[j]
				
				i = i + 1
				if data[self.pointer] != '\x02':
					raise Exception('Un-indexed array expected x02 after element, none found')
				
				i = i + 1
				j = j + 1
				print "---"
							
			print " <<<<<< leave parse_details ------- i: " + str(i)							
			return (return_array, i)
					
		# \x05 Indexed array
		elif(data[i] == self.DETAILS_TYPE_INDEXED_ARRAY):
			i += 1
			print 'found hash'
			
			(length, movement) = self.parse_number(data[i:])
			i += movement
			
			if DEBUG:
				print "hash: len(" + str(length) + ")"
			
			i += 1
			
			return_array = []
			nulls = 0
			curr_idx = 0
			
			while (curr_idx - nulls) < length:

				# get index and check for 'null' entries - THEY DO NOT COUNT AGAINST ARRAY LENGTH
				(idx, movement) = self.parse_number(data[i:])
				i += movement
				
				while idx > curr_idx:
					print "Packing a 'None'"
					return_array.append(None)
					curr_idx += 1
					nulls += 1
					
				curr_idx = idx
				(new_data, movement) = self.parse_details(data[i:])				
				i += movement
				
				return_array.append(new_data)
				
				i += 1
				
				print str(curr_idx) + " - " + str(nulls) + " < " + str(length)

			print "<<<<<< hasing done"
			pprint(return_array)
			
			return (return_array, i)
		
		elif(data[i] == self.DETAILS_TYPE_TINYINT):
			i = i + 1
			
			print "Tiny int = " + str(ord(data[i]))
			
			return (ord(data[i]), i + 1)
		
		#\x07 Big Integer
		elif(data[i] == self.DETAILS_TYPE_BIGINT):
			i = i + 1
			
			hex_str = hex(ord(data[i])) + str(hex(ord(data[i+1]))[2:]) + str(hex(ord(data[i+2]))[2:]) + str(hex(ord(data[i+3]))[2:])
			
			print "Big int = " + str(int(hex_str, 16))
			
			return (int(hex_str, 16), i+4)
		
		# \x09 VLF number found
		elif(data[i] == self.DETAILS_TYPE_VLF):
			i = i + 1
			
			if DEBUG:
				(value, movement) = self.parse_number(data[i:])
				print "Found VLF = " + str(value)
			
			(value, movement) = self.parse_number(data[i:])
			return (value, i + movement+1)
			
	def parse_number(self, data):
		i = 0

		# is the next byte going to be influential on this number?
		while ord(data[i]) & 0x80 == 0x80:
			i += 1

		value = ord(data[i])
		
		j = 0
		while j < i:		
			bit = ord(data[j]) & 0x7F
			value = value << 7
			value = value | bit
			j += 1
		
		if value & 1 == 1:
			value = (value >> 1) * -1
		else:
			value = (value >> 1)
		
		return (value, i)