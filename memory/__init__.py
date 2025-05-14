# coding=utf8
""" Memory

Handles internal sessions shared across requests
"""
from __future__ import annotations

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-03-15"

# Limit exports
__all__ = ['create', 'init', 'load']

# Ouroboros imports
from config import config
import jobject
import jsonb
from nredis import nr
from strings import random

# Pip imports
import json_fix

# Open redis connection
_moRedis = nr(config.memory.redis('session'))

def create(key: str = None, ttl: int = 0) -> _Memory:
	"""Create

	Returns a brand new session using the key given, else a UUID is generated

	Arguments:
		key (str): The key to use for the session
		ttl (uint): Time to live, a specific expiry time in seconds

	Returns:
		_Memory
	"""

	# Init the data with the expires time
	dData = { '__ttl': ttl }

	# If we were passed a key
	if key:

		# If it exists
		if _moRedis.exists(key):
			raise RuntimeError('memory_oc', key, 'key exists')

		# Set the key
		sKey = key

	# Else, loop till we get a key that works, which theoretically is always the
	#	first time, but on the off chance something breaks, let's have it fully
	#	break instead of running forever eating up resources.
	i = 0
	while True:

		# Generate a random key
		sKey = 's:%s' % random(32, [ 'aZ', '10', '!*' ])

		# If it doesn't exist, break out of the loop
		if not _moRedis.exists(sKey):
			break

		# Increment the count
		i += 1
		if i > 10:
			raise RuntimeError(
				'memory_oc', 'potential infinite loop in create()'
			)

	# Create a new Memory using the passed key, or a new UUID
	return _Memory(sKey, dData)

def load(key: str) -> _Memory:
	"""Load

	Loads an existing session from the cache

	Arguments:
		key (str): The unique id of an existing session

	Returns:
		_Memory
	"""

	# Fetch from Redis
	s = _moRedis.get(key)

	# If there's no session or it expired
	if s == None: return None

	# Make sure we have a string, not a set of bytes
	try: s = s.decode()
	except (UnicodeDecodeError, AttributeError): pass

	# Create a new instance with the decoded data
	return _Memory(key, jsonb.decode(s))

class _Memory(object):
	"""Memory

	A wrapper for the session data

	Extends:
		object
	"""

	def __init__(self, key: str, data: dict = {}):
		"""Constructor

		Intialises the instance, which is just setting up the dict

		Arguments:
			key (str): The key used to access or store the session
			data (dict): The data in the session

		Returns:
			_Memory
		"""

		# Store the key and data
		object.__setattr__(self, '__key', key)
		object.__setattr__(self, '__store', jobject(data))

	def __contains__(self, key: str):
		"""__contains__

		True if the key exists in the session

		Arguments:
			key (str): The field to check for

		Returns:
			bool
		"""
		return object.__getattribute__(self, '__store').__contains__(key)

	def __delitem__(self, k):
		"""__delete__

		Removes a key from a session

		Arguments:
			k (str): The key to remove

		Returns:
			None
		"""
		del object.__getattribute__(self, '__store')[k]

	def __getattr__(self, a: str) -> any:
		"""__getattr__

		Gives object notation access to get the internal dict keys

		Arguments:
			a (str): The attribute to get

		Raises:
			AttributeError

		Returns:
			any
		"""
		try:
			return object.__getattribute__(self, '__store')[a]
		except KeyError:
			raise AttributeError(a, '%s not in Memory instance' % a)

	def __getitem__(self, k):
		"""__getitem__

		Returns the given key

		Arguments:
			k (str): The key to return

		Returns:
			any
		"""
		return object.__getattribute__(self, '__store').__getitem__(k)

	def __iter__(self):
		"""__iter__

		Returns an iterator for the internal dict

		Returns:
			iterator
		"""
		return object.__getattribute__(self, '__store').__iter__()

	def __json__(self):
		"""__json__

		Returns a dict representation of the session

		Returns:
			dict
		"""
		return {
			'__key': object.__getattribute__(self, '__key'),
			'__store': object.__getattribute__(self, '__store')
		}

	def __len__(self):
		"""__len__

		Return the length of the internal dict

		Returns:
			uint
		"""
		return object.__getattribute__(self, '__store').__len__()

	def __setattr__(self, a: str, v: any) -> None:
		"""__setattr__

		Gives object notation access to set the internal dict keys

		Arguments:
			a (str): The key in the dict to set
			v (any): The value to set on the key
		"""
		object.__getattribute__(self, '__store').__setitem__(a, v)

	def __setitem__(self, k, v):
		"""__setitem__

		Sets the given key

		Arguments:
			k (str): The key to set
			v (any): The value for the key
		"""
		object.__getattribute__(self, '__store').__setitem__(k, v)

	def __str__(self):
		"""__str__

		Returns a string representation of the internal dict

		Returns:
			str
		"""
		return object.__getattribute__(self, '__store').__str__()

	def close(self):
		"""Close

		Deletes the session from the cache

		Returns:
			None
		"""
		_moRedis.delete(object.__getattribute__(self, '__key'))

	def extend(self):
		"""Extend

		Keep the session alive by extending it's expire time by the internally \
		set expire value, or else by the global one set for the module

		Returns:
			None
		"""

		# If the expire time is 0, do nothing
		if object.__getattribute__(self, '__store')['__ttl'] == 0:
			return

		# Extend the session in Redis
		_moRedis.expire(
			object.__getattribute__(self, '__key'),
			object.__getattribute__(self, '__store')['__ttl']
		)

	def key(self):
		"""Key

		Returns the key of the session

		Returns:
			str
		"""
		return object.__getattribute__(self, '__key')

	def save(self):
		"""Save

		Saves the current session data in the cache

		Returns:
			None
		"""

		# If we have no expire time, set forever
		if object.__getattribute__(self, '__store')['__ttl'] == 0:
			_moRedis.set(
				object.__getattribute__(self, '__key'),
				jsonb.encode(object.__getattribute__(self, '__store'))
			)

		# Else, set to expire
		else:
			_moRedis.setex(
				object.__getattribute__(self, '__key'),
				object.__getattribute__(self, '__store')['__ttl'],
				jsonb.encode(object.__getattribute__(self, '__store'))
			)