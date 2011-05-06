from pprint import pprint
from mpyq import MPQArchive

from sc2replaylib.parsers.details import DetailsParser

class Replay:
	
	teams = []
	
	timestamp = None
	timezone = None
	
	_replayFile = None
	
	FILE_NAME_DETAILS = 'replay.details'
	
	def __init__(self, _replayFile):
		
		try:
			archive = MPQArchive(_replayFile)
			files = archive.extract()

			for file_name, data in files.iteritems():
				if(file_name == self.FILE_NAME_DETAILS):
					
					details_parser = DetailsParser(data)
					raw_details = details_parser.parse()

					pprint(raw_details)

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