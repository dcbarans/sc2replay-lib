#! /usr/bin/env python

import argparse
from sc2replaylib import Replay

parser = argparse.ArgumentParser(
		description='This is a console adapter to work with SC2Replaylib library.')
parser.add_argument('replayFile', type=file)

args = parser.parse_args()

Replay.Replay(args.replayFile.name)