import io, codecs
from pprint import pprint
from mpyq import MPQArchive

from parsers.attributes import AttributesParser
from parsers.details import DetailsParser

class Replay:
	
	teams = []
	
	timestamp = None
	timezone = None
	
	_replayFile = None
	
	filenames = { 'attributes': 'replay.attributes.events', 'details': 'replay.details'}
	FILE_NAME_DETAILS = 'replay.details'
	
	def __init__(self, _replayFile):
		
		try:
			archive = MPQArchive(_replayFile)
			files = archive.extract()

			for file_name, data in files.iteritems():
				if(file_name == self.filenames['attributes']):
					attributes_parser = AttributesParser(data)
					raw_attributes = attributes_parser.parse()
					
					pprint(raw_attributes)
					
				if(file_name == self.filenames['details']):					
					details_parser = DetailsParser(data)
					raw_details = details_parser.parse()

					#pprint(raw_details)

		except IOError as (errno, strerror):
			print strerror
			

class Team:
	
	players = []
	
	isWinner = False
	
class Player:
	
	battlenet_id = None
	race = None
	color = None
	handycap = None