from pprint import pprint

from mpyq import MPQArchive

from sc2replaylib import Sc2replaylibException
from parsers.attributes import AttributesParser
from parsers.details import DetailsParser

class Replay:
	
	filenames = { 'attributes': 'replay.attributes.events', 'details': 'replay.details'}


	def timestamp(self):
		return None
		
	def timezone(self):
		return None

	def __init__(self, replay_file):
		
		self.teams 				= []
		self.replay_file		= replay_file
		
		self.details_parser		= None
		self.attributes_parser 	= None

		self.global_attributes	= None

		
		try:
			archive = MPQArchive(_replayFile.name)
			files = archive.extract()

			for file_name, data in files.iteritems():
				if(file_name == self.filenames['attributes']):
					self.attributes_parser = AttributesParser(data)
						
				if(file_name == self.filenames['details']):
					self.details_parser = DetailsParser(data)
		
			# pull out global attributes and register them to the instance
			self.global_attributes = self.player_attributes(16, self.raw_attributes)
			
			pprint(self.global_attributes)
		
			match_teams = self.get_global_attribute(2001)
			match_num_teams = 3

			if match_teams == '1v1':
				match_teams_lookup_attribute = 2002
				
			elif match_teams == '2v2':
				match_teams_lookup_attribute = 2003
				
			elif match_teams == '3v3':
				match_teams_lookup_attribute = 2004
				
			elif match_teams == '4v4':
				match_teams_lookup_attribute = 2005
				
			elif match_teams == 'FFA':
				match_teams_lookup_attribute = 2006
				match_num_teams = 10
				
			elif match_teams == '6v6':
				match_teams_lookup_attribute = 2008
			
			# create the teams before the players
			for i in range(match_num_teams):
				self.teams.append(Team(i+1))
			
			# actually build up the player object from parsed values			
			for i, player_details in enumerate(self.raw_details[0]):
				pprint(player_details)
				
				p = Player(player_details, self.player_attributes(i+1, self.raw_details))
								
				# team
				player_team = p.get_attribute(match_teams_lookup_attribute)								
				self.teams[int(player_team[1])-1].players.append(p)
						
		except IOError as (errno, strerror):
			print strerror
	
	def global_attribute(self, key):
		for attr in self.player_attributes(16):
			if attr[1] == key:
				return attr[3]

		# no attribute found!
		raise Sc2replaylibException("no global attribute found with key '%d'" % (key))
	
	def player_attributes(self, player_num):
		rc = []
		attributes = self.attributes_parser.parse()
		for attrib in attributes:
			if attrib[2] == player_num:
				rc.append(attrib)
		return rc

class Team:
	
	OUTCOME_UNKNOWN	= 0
	OUTCOME_WIN		= 1
	OUTCOME_LOSS	= 2
		
	def __init__(self, team_number):
		self.players = []
		self.number = team_number
				
	def outcome(self):
		outcome = self.OUTCOME_UNKNOWN
		for p in self.players:
			if outcome == self.OUTCOME_UNKNOWN and p.outcome != self.OUTCOME_UNKNOWN:
				outcome = p.outcome
			elif p.outcome != outcome:
				return self.OUTCOME_UNKNOWN
		return outcome
	
class Player:
	
	RACE_TERRAN			= 'Terran'
	RACE_PROTOSS		= 'Protoss'
	RACE_ZERG			= 'Zerg'
	RACE_RAND_TERRAN	= 'Rand-Terran'
	RACE_RAND_PROTOSS	= 'Rand-Protoss'
	RACE_RAND_ZERG		= 'Rand-Zerg'

	OUTCOME_UNKNOWN	= 0
	OUTCOME_WIN		= 1
	OUTCOME_LOSS	= 2
	
	HUMAN_COLORS = {
		'tc01': 'Red',
		'tc02': 'Blue',
		'tc03': 'Teal',
		'tc04': 'Purple',
		'tc05': 'Yellow',
		'tc06': 'Orange',
		'tc07': 'Green',
		'tc08': 'Light Pink',
		'tc09': 'Violet',
		'tc10': 'Light Grey',
		'tc11': 'Dark Green',
		'tc12': 'Brown',
		'tc13': 'Light Green',
		'tc14': 'Dark Grey',
		'tc15': 'Pink'
	}
	
	def __init__(self, details, attributes):
		self._details		= details
		self._attributes	= attributes

		self.handle			= None
		self.bnet_id		= None
		self.race			= None
		self.color_argb		= None
		self.colot_type		= None

		self.handicap		= None
		self.outcome		= self.OUTCOME_UNKNOWN
		
	def handle(self):
		return self._details[0]
		
	def bnet_id(self):
		return self._details[1]
		
	def race(self):
		race_attribute = self.get_attribute(3001)
		if race_attribute == 'RAND':
			if self._details[2] == 'Terran':
				return self.RACE_RAND_TERRAN
			
			elif self._details[2] == 'Protoss':
				return self.RACE_RAND_PROTOSS
			
			elif self._details[2] == 'Zerg':
				return self.RACE_RAND_PROTOSS
		
		elif race_attribute == 'Terr':
			return self.RACE_TERRAN
			
		elif race_attribute == 'Prot':
			return self.RACE_PROTOSS
		
	def color_argb(self):
		return self._details[3]
		
	def color_human_friendly(self):
		return self.HUMAN_COLORS[self.get_attribute(3002)]	
		
	def handicap(self):
		return	self._details[6]
		
	def outcome(self):
		return self._details[8]
	
	def get_attribute(self, key):
		for attr in self._attributes:
			if attr[1] == key:
				return attr[3]
		
		# no attribute found!
		raise Sc2replaylibException("no attribute found for player '%d' with key '%d'" % (attr[2], key))