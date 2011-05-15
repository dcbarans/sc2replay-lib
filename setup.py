import setuptools

setuptools.setup(
	name="sc2replay-lib",
	version="0.1",
	license="MPL 1.1",
	author="Dominic Baranski",
	author_email="dominic.baranski@gmail.com",
	url="https://github.com/dcbarans/sc2replay-lib",
	description="Basic library for reading details about a Blizzard (TM) StarCraft(TM) 2 replay file",
	long_description=''.join(open("README.txt").readlines()),
	keywords=["starcraft", "sc", "starcraft 2","sc2","parser","replay"],
	classifiers=[
			"Environment :: Console",
			"Development Status :: 4 - Beta",
			"Programming Language :: Python",
			"Programming Language :: Python :: 2.7",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)",
			"Natural Language :: English",
			"Operating System :: OS Independent",
			"Environment :: Other Environment",
			"Topic :: Utilities",
			"Topic :: Software Development :: Libraries",
			"Topic :: Games/Entertainment :: Real Time Strategy",
		],
	
	requires=['mpyq'],
	install_requires=['mpyq==0.1.5'],
	packages=['sc2replaylib', 'sc2replaylib.parsers'],
)