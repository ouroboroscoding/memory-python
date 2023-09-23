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
from jobject import jobject
import jsonb
from nredis import nr

# Python imports
import uuid

# Open redis connection
_moRedis = _moRedis = nr(config.memory.redis('session'))

def create(id: str = None, ttl: int = 0) -> _Memory:
	"""Create

	Returns a brand new session using the ID given, if no ID is passed, one is \
	generated

	Arguments:
		id (str): The ID to use for the session
		ttl (uint): Time to live, a specific expiry time in seconds

	Returns:
		_Memory
	"""

	# Init the data with the expires time
	dData = { '__ttl': ttl }

	# Create a new Memory using a UUID as the id
	return _Memory(id and id or uuid.uuid4().hex, dData)

def load(id: str) -> _Memory:
	"""Load

	Loads an existing session from the cache

	Arguments:
		id (str): The unique id of an existing session

	Returns:
		_Memory
	"""

	# Fetch from Redis
	s = _moRedis.get(id)

	# If there's no session or it expired
	if s == None: return None

	# Make sure we have a string, not a set of bytes
	try: s = s.decode()
	except (UnicodeDecodeError, AttributeError): pass

	# Create a new instance with the decoded data
	return _Memory(id, jsonb.decode(s))

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
		self.__key = key
		self.__store = jobject(data)

	def __contains__(self, key: str):
		"""__contains__

		True if the key exists in the session

		Arguments:
			key (str): The field to check for

		Returns:
			bool
		"""
		return self.__store.__contains__(key)

	def __delitem__(self, k):
		"""__delete__

		Removes a key from a session

		Arguments:
			k (str): The key to remove

		Returns:
			None
		"""
		del self.__store[k]

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
			self.__store.__getitem__(a)
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
		return self.__store.__getitem__(k)

	def __iter__(self):
		"""__iter__

		Returns an iterator for the internal dict

		Returns:
			iterator
		"""
		return self.__store.__iter__()

	def __len__(self):
		"""__len__

		Return the length of the internal dict

		Returns:
			uint
		"""
		return self.__store.__len__()

	def __setattr__(self, a: str, v: any) -> None:
		"""__setattr__

		Gives object notation access to set the internal dict keys

		Arguments:
			a (str): The key in the dict to set
			v (any): The value to set on the key
		"""
		self.__setitem__(a, v)

	def __setitem__(self, k, v):
		"""__setitem__

		Sets the given key

		Arguments:
			k (str): The key to set
			v (any): The value for the key

		Returns:
			None
		"""
		self.__store.__setitem__(k, v)

	def __str__(self):
		"""__str__

		Returns a string representation of the internal dict

		Returns:
			str
		"""
		return self.__store.__str__()

	def close(self):
		"""Close

		Deletes the session from the cache

		Returns:
			None
		"""
		_moRedis.delete(self.__key)

	def extend(self):
		"""Extend

		Keep the session alive by extending it's expire time by the internally \
		set expire value, or else by the global one set for the module

		Returns:
			None
		"""

		# If the expire time is 0, do nothing
		if self.__store['__ttl'] == 0:
			return

		# Extend the session in Redis
		_moRedis.expire(self.__key, self.__store['__ttl'])

	def key(self):
		"""Key

		Returns the key of the session

		Returns:
			str
		"""
		return self.__key

	def save(self):
		"""Save

		Saves the current session data in the cache

		Returns:
			None
		"""

		# If we have no expire time, set forever
		if self.__store['__ttl'] == 0:
			_moRedis.set(
				self.__key, jsonb.encode(self.__store)
			)

		# Else, set to expire
		else:
			_moRedis.setex(
				self.__key, self.__store['__ttl'], jsonb.encode(self.__store)
			)