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

# Python imports
import uuid

# Pip imports
from jobject import jobject
import jsonb
from redis import StrictRedis

# Open redis connection
_moRedis: StrictRedis = None
_muiExpire: int = 0

def create(id: str = None, expires: int = None) -> _Memory:
	"""Create

	Returns a brand new session using the ID given, if no ID is passed, one is \
	generated

	Arguments:
		id (str): The ID to use for the session
		expires (uint): A specific expiry in seconds to override the global \
						one for this session

	Returns:
		_Memory
	"""

	# Init the data
	dData = {}

	# If we have an expires time
	if expires:
		dData['__expire'] = expires

	# Create a new Memory using a UUID as the id
	return _Memory(id and id or uuid.uuid4().hex, dData)

def init(conf: dict, expire: int = 0) -> None:
	"""Init

	Initialises the module

	Arguments:
		conf (dict): The Redis configuration
		expire (uint): Length in seconds for any new session to remain active

	Returns:
		None
	"""

	# Pull in the module variable
	global _moRedis, _muiExpire

	# Create the Redis connection
	_moRedis = StrictRedis(**conf)

	# Store the expire time
	_muiExpire = expire

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
	"""

	def __init__(self, id: str, data: dict = {}):
		"""Constructor

		Intialises the instance, which is just setting up the dict

		Arguments:
			id (str): The ID of the session
			data (dict): The data in the session

		Returns:
			_Memory
		"""
		self.__id = id
		self.__store = jobject(data)

	def __call__(self) -> jobject:
		"""Call

		Overwrites python magic method __call__ to all the memory to be called \
		and return the internal store of data associated

		Returns:
			A dictionary like object of the data stored in the memory
		"""
		return self.__store

	def close(self):
		"""Close

		Deletes the session from the cache

		Returns:
			None
		"""
		_moRedis.delete(self.__id)

	def extend(self):
		"""Extend

		Keep the session alive by extending it's expire time by the internally \
		set expire value, or else by the global one set for the module

		Returns:
			None
		"""

		# Use internal time if we have one, else use the global
		iExpire = '__expire' in self.__store and \
					self.__store['__expire'] or \
					_muiExpire

		# If the expire time is 0, do nothing
		if iExpire == 0:
			return

		# Extend the session in Redis
		_moRedis.expire(self.__id, iExpire)

	def id(self):
		"""ID

		Returns the ID of the session

		Returns:
			str
		"""
		return self.__id

	def save(self):
		"""Save

		Saves the current session data in the cache

		Returns:
			None
		"""

		# Use internal time if we have one, else use the global
		iExpire = '__expire' in self.__store and \
					self.__store['__expire'] or \
					_muiExpire

		# If we have no expire time, set forever
		if iExpire == 0:
			_moRedis.set(self.__id, jsonb.encode(self.__store))

		# Else, set to expire
		else:
			_moRedis.setex(self.__id, _muiExpire, jsonb.encode(self.__store))