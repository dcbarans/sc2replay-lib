#! /usr/bin/env python

import argparse
from sc2replaylib.Replay import Replay
import pprint

parser = argparse.ArgumentParser(
		description='This is a console adapter to work with SC2Replaylib library.')
parser.add_argument('replayFile', type=file)

args = parser.parse_args()

# basic replay here
replay = Replay(args.replayFile)
#pprint.pprint(replay)