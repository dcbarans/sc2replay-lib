from mpyq import MPQArchive

from sc2replaylib import Sc2replaylibException
from sc2replaylib.parsers.attributes import AttributesParser
from sc2replaylib.parsers.details import DetailsParser

class Replay:
	"""
	This class, once initialized with a valid replay file, contains all the data about the given replay
	"""

	GAME_TEAMS = {
		'1v1': '1v1',
		'2v2': '2v2',
		'3v3': '3v3',
		'4v4': '4v4',
		'6v6': '6v6',
		'FFA': 'Free for all',
		'Cust': 'Custom Game'
	}
	
	GAME_SPEED = {
		'Slow': 'Slow',
		'Slor': 'Slower',
		'Norm': 'Normal',
		'Fasr': 'Faster',
		'Fast': 'Fast'
	}
	
	GAME_MATCHING = {
		'Priv':	'Private',
		'Amm':	'Auto Match Maker',
		'Pub':	'Public'
	}	
	
	FILES = {
		'attributes':	'replay.attributes.events',
		'details':		'replay.details'
	}

	def __init__(self, replay_file):
		"""
		Args:
			replay_file (file): This is what the user believes to be a starcraft 2 replay file.
		"""
		self.teams 				= []
		self.replay_file		= replay_file
		
		self.parsers			= {}

		try:
			archive = MPQArchive(self.replay_file)
						
			files = archive.extract()

			# bootstrap the right parsers, expand here for different version parsing too
			
			self.parsers['header'] = DetailsParser(archive.header['user_data_header']['content'])
			
			for file_name, data in files.iteritems():
				if(file_name == self.FILES['attributes']):
					self.parsers[file_name] = AttributesParser(data)
						
				if(file_name == self.FILES['details']):
					self.parsers[file_name] = DetailsParser(data)
		
			teams = self.attribute(2001)
			num_teams = 2

			if teams == '1v1':
				teams_lookup_attribute = 2002
				
			elif teams == '2v2':
				teams_lookup_attribute = 2003
				
			elif teams == '3v3':
				teams_lookup_attribute = 2004
				
			elif teams == '4v4':
				teams_lookup_attribute = 2005
				
			elif teams == 'FFA':
				teams_lookup_attribute = 2006
				num_teams = 10
				
			elif teams == '6v6':
				teams_lookup_attribute = 2008
			
			# create the teams before the players
			for i in range(num_teams):
				self.teams.append(Team(i+1))
			
			# bootstrap the player object with some raw data
			for i, player_details in enumerate(self.parsers[self.FILES['details']].parse()[0]):
				
				player = Player(player_details, self.player_attributes(i+1))
								
				# team
				players_team = player.attribute(teams_lookup_attribute)								
				self.teams[int(players_team[1])-1].players.append(player)
				
		except IOError as (errno, strerror):
			print strerror
		
	def attribute(self, key):
		"""Get a single attribute by it's key

		This will fetch a *replay attribute* by its key.  A replay attribute is one that is concidered global
		to all players durring the match.  See [[]] for more information on global attributes.

		:param key: The attribute name to look for.
		:type key: String
		:rtype: A string or integer
		:raise Sc2ReplaylibException: If no attribute is found then this exception is raised
		"""

		attributes = self.attributes()
		for attr in attributes:
			if attr[1] == key:
				return attr[3]

		# no attribute found!
		raise Sc2replaylibException("no global attribute found with key '%d'" % (key))
	
	def player_attributes(self, player_num):
		"""Get all player attributes for a given player

		This function returns a list of player attributes that match the given player number.

		:param player_num: The player number, can be between 1 to 8
		:type player_num: Int
		:rtype: List
		"""

		rc = []
		attributes = self.parsers[self.FILES['attributes']].parse()
		for attrib in attributes:
			if attrib[2] == player_num:
				rc.append(attrib)
		return rc
	
	def attributes(self):
		"""Retrieve a list of *global attributes*"""

		return self.player_attributes(16)

	@property
	def game_teams(self):
		"""Holds the raw value for what kind of team layout the currently loaded replay has.

		This attribute holds the *raw* value exactly as it is retrieved from the replay file.  It can be of the following types:

		 * ``1v1`` --- Represents a one versus one
		 * ``2v2`` --- Represents a game with two teams composed of two players each
		 * ``3v3`` --- Represents a game with two teams composed of three players each
		 * ``4v4`` --- Represents a game with two teams composed of four players each
		 * ``FFA`` --- Represents a game with no teams, but can have anywhere from two to eight players
		 * ``Cust`` --- Represents a custom game where the regular starcraft 2 multiplayer rules do not apply

		:rtype: String --- Raw

		.. warning::
			Using the raw values is not recomended because they may change durring any given update.  It is recomended to run the output through
			the ``GAME_TEAMS`` global dict to retrieve a consistent value.

		"""

		return self.attribute(2001)
		
	@property
	def game_speed(self):
		"""Holds the raw game speed value for the currently loaded replay.

		This attribute holds the *raw* value exactly as it is retrieved from the replay file.  It can be of the following types:

		 * ``Slow`` --- Represents the slowest game speed available, Slow
		 * ``Slor`` --- Represents the 2nd slowest game speed, Slower
		 * ``Norm`` --- Represents the normal game speed, Normal
		 * ``Fasr`` --- Represents the 2nd fastest game speed, Faster
		 * ``Fast`` --- Represents the fastest game speed, Fast

		.. warning::
			Using the raw values is not recomended because they may change durring any given update.  It is recomended to run the output through
			the ``GAME_SPEED`` global dict to retrieve a consistent value.

		"""

		return self.attribute(3000)
	
	@property
	def game_matching(self):
		return self.attribute(3009)
	
	@property
	def map_human_friendly(self):
		return self.parsers[self.FILES['details']].parse()[1]

	@property
	def version(self):
		return self.parsers['header'].parse()[1][:4]

	@property
	def revision(self):
		return self.parsers['header'].parse()[1][4:5][0]

	@property
	def timestamp(self):
		from datetime import datetime
		return datetime.fromtimestamp((self.parsers[self.FILES['details']].parse()[5] - 116444735995904000) / 10**7)

	@property
	def timezone_offset(self):
		return (self.parsers[self.FILES['details']].parse()[6] / 10**7 ) / (60 * 60)

class Team:
	
	OUTCOME	= {
		0: "Unknown",
		1: "Won",
		2: "Lossed"
	}
		
	def __init__(self, team_number):
		self.players = []
		self.number = team_number
		
	@property		
	def outcome(self):
		outcome = self.OUTCOME[0]
		for p in self.players:
			if outcome == self.OUTCOME[0] and p.outcome != self.OUTCOME[0]:
				outcome = p.outcome
			elif p.outcome != outcome:
				return self.OUTCOME[0]
		return outcome
	
class Player:
	
	RACE = {
		'Terran':		'Terran',
		'Protoss':		'Protoss',
		'Zerg':			'Zerg',
		'Rand-Terran':	'Random Terran',
		'Rand-Protoss':	'Random Protoss',
		'Rand-Zerg':	'Random Zerg'
	}
	
	OUTCOME	= {
		0: "Unknown",
		1: "Won",
		2: "Lossed"
	}
	
	COLORS = {
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
	
	TYPE = {
		'Humn': 'Human',
		'Comp': 'Computer'
	}
	
	DIFFICULTY = {
		'Easy': 'Easy',
		'VyEy': 'Very Easy',
		'Medi': 'Medium',
		'VyHd': 'Very Hard',
		'Insa': 'Insane'
	}
	
	def __init__(self, details, attributes):
		self.details	= details
		self.attributes	= attributes

	@property
	def type(self):
		return self.attribute(500)

	@property
	def handle(self):
		return self.details[0]
		
	@property
	def bnet_id(self):
		return self.details[1]
		
	@property
	def race(self):
		race = self.attribute(3001)
		if race == 'RAND':
			if self.details[2] == 'Terran':
				return 'Rand-Terran'
			
			elif self.details[2] == 'Protoss':
				return 'Rand-Protoss'
			
			elif self.details[2] == 'Zerg':
				return 'Rand-Zerg'
		
		elif race == 'Terr':
			return 'Terran'
			
		elif race == 'Prot':
			return 'Protoss'
			
		elif race == 'Zerg':
			return 'Zerg'
		
	@property
	def color_argb(self):
		return self.details[3]
		
	@property
	def color_name(self):
		return self.COLORS[self.attribute(3002)]
		
	@property
	def handicap(self):
		return	self.details[6]
	
	@property	
	def outcome(self):
		return self.details[8]
	
	def attribute(self, key):
		for attr in self.attributes:
			if attr[1] == key:
				return attr[3]
		
		# no attribute found!
		raise Sc2replaylibException("no attribute found for player '%d' with key '%d'" % (attr[2], key))
