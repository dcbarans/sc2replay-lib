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
	
	pointer = 0
	
	def __init__(self, filename):
		
		try:
			archive = MPQArchive(filename)
			files = archive.extract()
			
			for file_name, data in files.iteritems():
				if(file_name == self.FILE_NAME_DETAILS):
					print self.parse_details(data)
			
		except IOError as (errno, strerror):
			print strerror
	
	'''
	Recursive function to parse_details
	'''
	def parse_details(self, data):
	
		i = 0
	
		if DEBUG:
			print " >>>>>> enter parse_details ------- pointer: " + str(self.pointer)
			pprint(data[self.pointer])
	
		# \x02 binary data
		if(data[i] == self.DETAILS_TYPE_BIN):
		
			print 'found bin'
		
			i = i + 1
			length = self.parse_number(data[i])
			
			i = i + 1
			if DEBUG:
				print "Bin: len(" + str(length) + ") = " + data[i : i + length]
			
			
			self.pointer = self.pointer + i

			print " <<<<<< leave parse_details ------- pointer: " + str(self.pointer)
			return data[i : i + length]
			
		# \x04 array
		elif(data[i] == self.DETAILS_TYPE_ARRAY):
		
			print 'found array'
		
			# \x01 should follow identifyer...
			i = i + 1
			if data[i] != '\x01':
				raise Exception('This should have been \x01 in array')

			# ... then \x00					
			i = i + 1
			if data[i] != '\x00':
				raise Exception('This should have been \x00 in array')
				
			# ... then length
			i = i + 1
			length = self.parse_number(data[i])
			
			if DEBUG:
				print "Array: len(" + str(length) + ")"
			
			# move up i to the data!
			i = i + 1
			j = 0
			return_array = []
			
			while j < length:
				
				print 'array looping :' + str(j) + " < " + str(length)
			
				print '+++' + str(self.pointer) + " + " + str(i) + "+++"
				
				self.pointer = self.pointer + i
				return_array.append(self.parse_details(data[self.pointer:]))
				
				print '-----------pointer: ' + str(self.pointer)
				
				if DEBUG:
					print "returned: " + return_array[j]
				
				self.pointer = self.pointer + 1
				if data[self.pointer] != '\x02':
					raise Exception('Un-indexed array expected x02 after element, none found')
				
				self.pointer = self.pointer + 1
				j = j + 1
							
			print " <<<<<< leave parse_details ------- pointer: " + str(self.pointer)							
			return return_array
					
		# \x05 Indexed array
		elif(data[i] == self.DETAILS_TYPE_INDEXED_ARRAY):
			i = i + 1
			
			print 'found hash'
			
			length = self.parse_number(data[i])
			
			if DEBUG:
				print "hash: len(" + str(length) + ") = "
			
			i = i + 1

			# index 0 should follow array length
			curr_idx = self.parse_number(data[i])
							
			i = i + 1
			
			return_array = []
			
			while curr_idx < length:
			
				print 'hash looping: ' + str(curr_idx) + " < " + str(length)
				
				self.pointer = self.pointer + i
				return_array.append(self.parse_details(data[self.pointer:]))
				
				self.pointer = self.pointer + 1
				curr_idx = self.parse_number(data[i])

			print " <<<<<< leave parse_details ------- pointer: " + str(self.pointer)
			return return_array
			
	def parse_number(self, data):
	
		if (ord(data) & 1):
			value = (ord(data) >> 1) * -1
		else:
			value = (ord(data) >> 1)
			
		return value

#		i = 0
#		while data[i] == '\x80':
#			i = i+1