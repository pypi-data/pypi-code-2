#!python

# $Id: _enum.py 960 2009-04-02 15:37:29Z jaraco $

"""
This enum module fills a different niche than the
enum package as found in PyPI.  In particular, it allows
access to the values, allowing them to be enumerate and
compared against integers

>>> class MyEnum(SpecEnum):
...   x = 1
...   y = 2
...   z = 40

>>> 'z' in MyEnum.keys()
True
>>> MyEnum.x == 1
True

You can retrieve the enumerated values as a dictionary also:
>>> MyEnum.dictionary() == {'x': 1, 'y': 2, 'z': 40}
True

"""

class SpecEnum(object):

	@classmethod
	def dictionary(cls):
		"Return all of the class attributes that do not begin with _"
		items = cls.__dict__.items()
		pub_items = (
			(key, value)
			for (key, value) in items
			if not key.startswith('_')
			)
		return dict(pub_items)

	@classmethod
	def keys(cls):
		return cls.dictionary().keys()
		
	@classmethod
	def values(cls):
		return cls.dictionary().values()

class CommandTypes(SpecEnum):
	direct = 0
	system = 1
	reply = 2

class OutputPort(SpecEnum):
	a = 0
	b = 1
	c = 2
	all = 0xff

class OutputMode(SpecEnum):
	motor_on = 1
	brake = 2
	regulated = 4

# RegulationMode = Enum('idle', 'motor_speed', 'motor_sync')
class RegulationMode(SpecEnum):
	idle = 0
	motor_speed = 1
	motor_sync = 2

class RunState(SpecEnum):
	idle = 0x00
	rampup = 0x10
	running = 0x20
	rampdown = 0x40

class SensorType(SpecEnum):
	no_sensor = 0
	switch = 1
	temperature = 2
	reflection = 3
	angle = 4
	light_active = 5
	light_inactive = 6
	sound_db = 7
	sound_dba = 8
	custom = 9
	lowspeed = 0xa
	lowspeed_9v = 0xb
	no_of_sensor_types = 0xc

class SensorMode(SpecEnum):
	raw = 0
	boolean = 0x20
	transition_count = 0x40
	period_counter = 0x60
	pct_full_scale = 0x80
	celcius = 0xA0
	fahrenheit = 0xC0
	angle_steps = 0xE0
	slope_mask = 0x1F
	mode_mask = 0xE0
	
