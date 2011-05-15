#!/usr/bin/env python

import argparse
from sc2replaylib.replay import Replay, Team, Player
from pprint import pprint

from sc2replaylib.replay import Replay, Team, Player

parser = argparse.ArgumentParser(
		description='This is a console adapter to work with SC2Replaylib library.')
parser.add_argument('replayFile', type=file)

args = parser.parse_args()

# some example usages----

# basic replay here
replay = Replay(args.replayFile)

#raw data on the replay file-----
pprint(replay.details_parser.parse())
pprint(replay.attributes_parser.parse())

#-------

# run output of game_speed through human readable list of values
print replay.GAME_SPEED[replay.game_speed]

# raw output of game_teams attribute (could be ugly-ish)
print replay.game_teams

# running output through another included list
print replay.GAME_MATCHING[replay.game_matching]

# datetime object returned with date match was played
print replay.timestamp

# timezone offset as integer
print replay.timezone_offset


#-------

#pull team information
print "there are %d teams" % len(replay.teams)

# pull team win/loss info
print "Team 1 %s" % Team.OUTCOME[replay.teams[0].outcome]
print "Team 2 %s" % Team.OUTCOME[replay.teams[1].outcome]


#-------

print "There are %d players on team 1" % len(replay.teams[0].players)

player = replay.teams[0].players[0]
print "%s the %s %s playing as the %s %s" % (
	player.handle,
	player.TYPE[player.type],
	player.OUTCOME[player.outcome],
	player.color_name,
	player.RACE[player.race])
