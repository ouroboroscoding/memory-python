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
__all__ = [ 'close', 'create', 'load' ]

# Ouroboros imports
from config import config
import jobject
import jsonb
from nredis import nr
from strings import random
from tools import combine

# Python imports
from copy import deepcopy

# Pip imports
import json_fix

# Open redis connection
_moRedis = nr(config.memory.redis('session'))

def close(key: str):
	"""Close

	Deletes the session from the cache
	"""
	_moRedis.delete(key)

def create(key: str = None, ttl: int = 0, data = None) -> _Memory:
	"""Create

	Returns a brand new session using the key given, else a random key is
	generated.

	Arguments:
		key (str): The key to use for the session
		ttl (uint): Time to live, a specific expiry time in seconds
		data (dict): Initial data in the session

	Returns:
		_Memory
	"""

	# If the ttl is not an unsigned int
	if isinstance(ttl, bool) or not isinstance(ttl, int) or ttl < 0:
		raise ValueError('ttl must be an unsigned int')

	# Generate the data to store by adding the TTL
	dData = (
		data is None
			and { '__ttl': ttl }
			or combine(data, { '__ttl': ttl })
	)

	# If we were passed a key
	if key:

		# If it exists
		if _moRedis.exists(key):
			raise RuntimeError(f'memory_oc: "{key}" exists')

		# Set the key
		sKey = key

	# Else, loop till we get a key that works, which theoretically is always the
	#	first time, but on the off chance something breaks, let's have it fully
	#	break instead of running forever eating up resources.
	else:
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
					'memory_oc, potential infinite loop in create()'
				)

	# Create a new Memory using the passed key, or a new random string
	return _Memory(sKey, dData)

def load(key: str) -> _Memory | None:
	"""Load

	Loads an existing session from the cache, or None if it doesn't exist.

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

	A wrapper for the session data.

	Extends:
		object
	"""

	def __init__(self, key: str, data: dict | None = None) -> _Memory:
		"""Constructor

		Intialises the instance, which is just setting up the dict

		Arguments:
			key (str): The key used to access or store the session
			data (dict): The data in the session

		Returns:
			_Memory
		"""

		# If no data passed, init an empty dict
		if data is None:
			data = { }

		# Store the key and data
		object.__setattr__(self, '__key', key)
		object.__setattr__(self, '__store', jobject(data))

	def __contains__(self, key: str):
		"""__contains__

		True if the key exists in the session.

		Arguments:
			key (str): The field to check for

		Returns:
			bool
		"""
		return object.__getattribute__(self, '__store').__contains__(key)

	def __delitem__(self, k: str):
		"""__delete__

		Removes a key from a session.

		Arguments:
			k (str): The key to remove
		"""

		# Don't allow special keys to be changed
		if isinstance(k, str) and k.startswith('__'):
			raise KeyError(f'{k} is read-only')

		del object.__getattribute__(self, '__store')[k]

	def __getattr__(self, a: str) -> any:
		"""__getattr__

		Gives object notation access to get the internal dict keys.

		Arguments:
			a (str): The attribute to get

		Raises:
			AttributeError

		Returns:
			any
		"""

		# Check for store, likely to exist, but necessary for some libraries
		try:
			dStore = object.__getattribute__(self, '__store')
		except AttributeError:
			raise AttributeError(a) from None

		# Try the actual attribute
		try:
			return dStore[a]
		except KeyError:
			raise AttributeError(f'{a} not in Memory instance') from None

	def __getitem__(self, k):
		"""__getitem__

		Returns the given key.

		Arguments:
			k (str): The key to return

		Returns:
			any
		"""
		return object.__getattribute__(self, '__store').__getitem__(k)

	def __iter__(self):
		"""__iter__

		Returns an iterator for the internal dict.

		Returns:
			iterator
		"""
		return object.__getattribute__(self, '__store').__iter__()

	def __json__(self):
		"""__json__

		Returns a dict representation of the session.

		Returns:
			dict
		"""
		return {
			'__key': object.__getattribute__(self, '__key'),
			'__store': deepcopy(object.__getattribute__(self, '__store'))
		}

	def __len__(self):
		"""__len__

		Return the length of the internal dict.

		Returns:
			uint
		"""
		return object.__getattribute__(self, '__store').__len__()

	def __setattr__(self, a: str, v: any) -> None:
		"""__setattr__

		Gives object notation access to set the internal dict keys.

		Arguments:
			a (str): The key in the dict to set
			v (any): The value to set on the key
		"""

		# Don't allow special keys to be changed
		if a.startswith('__'):
			raise KeyError(f'{a} is read-only')

		# Set the item
		object.__getattribute__(self, '__store').__setitem__(a, v)

	def __setitem__(self, k: str, v: any):
		"""__setitem__

		Sets the given key.

		Arguments:
			k (str): The key to set
			v (any): The value for the key
		"""

		# Don't allow special keys to be changed
		if isinstance(k, str) and k.startswith('__'):
			raise KeyError(f'{k} is read-only')

		# Set the item
		object.__getattribute__(self, '__store').__setitem__(k, v)

	def __str__(self):
		"""__str__

		Returns a string representation of the internal dict.

		Returns:
			str
		"""
		return object.__getattribute__(self, '__store').__str__()

	def close(self):
		"""Close

		Deletes the session from the cache.
		"""
		_moRedis.delete(object.__getattribute__(self, '__key'))

	def extend(self):
		"""Extend

		Keep the session alive by extending it's expire time by the internally
		set expire value, or else by the global one set for the module.
		"""

		# Get the store
		dStore = object.__getattribute__(self, '__store')

		# If the expire time is 0, do nothing
		if dStore['__ttl'] == 0:
			return

		# Extend the session in Redis
		_moRedis.expire(object.__getattribute__(self, '__key'), dStore['__ttl'])

	def key(self) -> str:
		"""Key

		Returns the key of the session.

		Returns:
			str
		"""
		return object.__getattribute__(self, '__key')

	def save(self):
		"""Save

		Saves the current session data in the cache.
		"""

		# Get the store
		dStore = object.__getattribute__(self, '__store')

		# Encode it
		dJSON = jsonb.encode(dStore)

		# If we have no expire time, set forever
		if dStore['__ttl'] == 0:
			_moRedis.set(object.__getattribute__(self, '__key'), dJSON)

		# Else, set to expire
		else:
			_moRedis.setex(
				object.__getattribute__(self, '__key'),
				dStore['__ttl'],
				dJSON
			)

	def ttl(self, ttl: int | None = None) -> int | None:
		"""TTL

		Getter / Setter for the Time To Live in seconds of the session.

		Arguments:
			ttl (uint | None): Do not set to fetch the current value, set to 0
				(zero) for a session that never expires, set to anything greater
				than 0 (zero) to have it expired in `ttl` seconds

		Returns:
			uint | None
		"""

		# Get the store
		dStore = object.__getattribute__(self, '__store')

		# If we are requesting the data
		if ttl is None:
			return dStore['__ttl']

		# If we didn't get a number, or it's below 0
		if isinstance(ttl, bool) or not isinstance(ttl, int) or ttl < 0:
			raise ValueError('ttl must be an unsigned int')

		# If the value hasn't changed
		if ttl != dStore['__ttl']:
			dStore['__ttl'] = ttl
			self.save()

	def update(self, other = (), /, **kwargs):
		"""Updated

		Merge key/value pairs into the session store. Works exactly like dict
		update().

		Arguments:
			other (dict, list, **kwargs): The additional keys and values to add
		"""

		# Run through each to guard against __ keys being set
		for k, v in dict(other, **kwargs).items():
			self[k] = v