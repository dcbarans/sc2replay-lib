from pprint import pprint

from mpyq import MPQArchive

from sc2replaylib import Sc2replaylibException
from parsers.attributes import AttributesParser
from parsers.details import DetailsParser

class Replay:
	
	teams				= []
	
	timestamp			= None
	timezone			= None
	
	_global_attributes	= None
	_replayFile			= None
	
	# store parsed values, no need to parse twice
	details = None
	attributes = None
	
	filenames = { 'attributes': 'replay.attributes.events', 'details': 'replay.details'}

	def get_global_attribute(self, key):
		for attr in self._global_attributes:
			if attr[1] == key:
				return attr[3]
		
		# no attribute found!
		raise Sc2replaylibException("no global attribute found with key '%d'" % (key))


	def __init__(self, _replayFile):
		
		try:
			archive = MPQArchive(_replayFile)
			files = archive.extract()

			for file_name, data in files.iteritems():
				
				if(file_name == self.filenames['attributes']):
					self.attributes = AttributesParser(data).parse()
					pprint(self.attributes)
	
				if(file_name == self.filenames['details']):
					self.details = DetailsParser(data).parse()
					pprint(self.details)
		
			# pull out global attributes
			self._global_attributes = self.player_attributes(16, self.attributes)
			
			pprint(self._global_attributes)
		
			match_teams = self.get_global_attribute(2001)
			match_num_teams = 2

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
			
			for i in range(match_num_teams):
				t = Team(i+1)
				self.teams.append(t)
			
			# actually build up the player object from parsed values			
			for i, player_details in enumerate(self.details[0]):
				pprint(player_details)
				
				p = Player()
				
				p._details		= player_details				
				p._attributes	= self.player_attributes(i+1, self.attributes)
				
				# username
				p.handle		= player_details[0]
				
				# battle net identification stuffs
				p.bnet_id		= player_details[1]
				
				# race
				race_attribute = p.get_attribute(3001)
				if race_attribute == 'RAND':
					if player_details[2] == 'Terran':
						p.race = p.RACE_RAND_TERRAN
					
					elif player_details[2] == 'Protoss':
						p.race = p.RACE_RAND_PROTOSS
					
					elif player_details[2] == 'Zerg':
						p.race = p.RACE_RAND_PROTOSS
				
				elif race_attribute == 'Terr':
					p.race = p.RACE_TERRAN
					
				elif race_attribute == 'Prot':
					p.race = p.RACE_PROTOSS
				
				# color
				p.color_argb	= player_details[3]
				p.color_type	= p.get_attribute(3002)
				
				p.handicap		= player_details[6]
				
				# team
				player_team = p.get_attribute(match_teams_lookup_attribute)
				
				print 'appending %s to team %d' % (p.handle, int(player_team[1])-1)
				self.teams[int(player_team[1])-1].players.append(p)
				
				print '--------------------------'
				
			for t in self.teams:
				print t
				
		except IOError as (errno, strerror):
			print strerror
	
	def player_attributes(self, player_num, attributes):
		rc = []
		for attrib in attributes:
			if attrib[2] == player_num:
				rc.append(attrib)
		return rc

class Team:
	
	OUTCOME_UNKNOWN	= 0
	OUTCOME_WIN		= 1
	OUTCOME_LOSS	= 2
	
	number	= None
	players = []
	
	def __init__(self, team_number):
		self.number = team_number
		
	def __str__(self):
		strr = ''
		for p in self.players:
			strr += p.handle + ' - '
		return strr
	
	
class Player:
	
	RACE_TERRAN			= 'Terran'
	RACE_PROTOSS		= 'Protoss'
	RACE_ZERG			= 'Zerg'
	RACE_RAND_TERRAN	= 'Rand-Terran'
	RACE_RAND_PROTOSS	= 'Rand-Protoss'
	RACE_RAND_ZERG		= 'Rand-Zerg'
	
	_details	= None
	_attributes	= None
	
	handle		= None
	bnet_id		= None
	race		= None
	color_argb	= None
	colot_type	= None
	
	handicap	= None
	
	win_status	= None
	
	def get_attribute(self, key):
		for attr in self._attributes:
			if attr[1] == key:
				return attr[3]
		
		# no attribute found!
		raise Sc2replaylibException("no attribute found for player '%d' with key '%d'" % (attr[2], key))
		
