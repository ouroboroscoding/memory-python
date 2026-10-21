# memory_oc
[![pypi version](https://img.shields.io/pypi/v/memory_oc.svg)](https://pypi.org/project/memory_oc) ![Custom License](https://img.shields.io/pypi/l/memory_oc.svg)

Provides methods for creating and managing sessions in [body_oc](https://pypi.org/project/body-oc/)
projects.

Please see [LICENSE](https://github.com/ouroboroscoding/memory-python/blob/main/LICENSE)
for further information.

See [Releases](https://github.com/ouroboroscoding/memory-python/blob/main/releases.md)
for changes from release to release.

## Contents
- [Module Install](#module-install)
- [Configuration](#configuration)
- [Methods](#methods)
  - [close](#close)
  - [create](#create)
  - [from_dict](#from_dict)
  - [load](#load)
- [Class](#class)
  - [close](#close-1)
  - [extend](#extend)
  - [key](#key)
  - [save](#save)
  - [to_dict](#to_dict)
  - [ttl](#ttl)
  - [update](#update)

## Module Install

### Requires
memory_oc requires python 3.10 or higher

### Install via pip
```bash
pip install memory_oc
```

[ [top](#memory_oc) / [contents](#contents) ]

## Configuration
Memory requires the use of a config_oc config.json file. See [config_oc](https://pypi.org/project/config-oc/)
for more info.

```json
{
  "memory": {
    "redis": "session"
  },

  "redis": {
    "session": {
      "host": "redis.mydomain.com",
      "db": 1
    }
  }
}
```

The `redis` section lists Redis connections by name and details to connect. Then
`memory.redis` specifies which connection to use to create the sessions on.

[ [top](#memory_oc) / [contents](#contents) ]

## Methods
Memory comes with four methods, to [`close`](#close), [`create`](#create),
[`from_dict`](#from_dict) and [`load`](#load) sessions.

### close
Immediately closes and deletes a session from Redis.

```python
import memory

# Closes the session by key
memory.close(somekey)
```

[ [top](#memory_oc) / [contents](#contents) / [methods](#methods) ]

### create
Creates a new session. Takes 3 optional arguments

| Argument | Type | Description |
| -------- | ---- | ----------- |
| `key` | str | The key to use to create the session in Redis. |
| `ttl` | unsigned integer | The time to live in seconds for the session. |
| `data` | dict | The initial data to be stored in the session. |

```python
import memory

# Creates a 10 minutes session
session = memory.create(ttl = 600, data = {
	'email': 'sam@somedomain.com',
	'name': 'Sam'
})

# Stores it in Redis
session.save()

# Returns the generated session key
return session.key()
```

[ [top](#memory_oc) / [contents](#contents) / [methods](#methods) ]

### from_dict
Returns a new instance generated from a dict returned by [`to_dict`](#instanceto_dict)

```python
import memory

# Load a session
session = memory.load(somekey)

# Convert to a dict
d = session.to_dict()

# Revert to a session
session_copy = memory.from_dict(d)
```

[ [top](#memory_oc) / [contents](#contents) / [methods](#methods) ]

### load
Loads a session from a passed key.

```python
import memory

# Loads the session data from Redis
session = memory.load(somekey)

# Change data
session['name'] = 'Samuel'

# Store it in Redis
session.save()
```

[ [top](#memory_oc) / [contents](#contents) / [methods](#methods) ]

## Class
The class is what is returned from the [`create`](#create),
[`from_dict`](#from_dict), and [`load`](#load) methods

### close
Closes the session in Redis, making it no longer available to anyone.

```python
import memory

# Load the session
session = memory.load(somekey)

# Close the session
session.close()
```

[ [top](#memory_oc) / [contents](#contents) / [class](#class) ]

### extend
Extends the TTL of the session by the initial TTL given.

```python
import memory

# Load the session
session = memory.load(somekey)

# Extend the session
session.extend()
```

[ [top](#memory_oc) / [contents](#contents) / [class](#class) ]

### key
Returns the key of the session.

```python
import memory

# Create the session
session = memory.create()

# Print the key
print(session.key())
```

[ [top](#memory_oc) / [contents](#contents) / [class](#class) ]

### save
Stores changes in Redis after updates.

```python
import memory

# Load a session
session = memory.load(somekey)

# Make changes
session['name'] = 'Samuel'

# Save changes
session.save()
```

[ [top](#memory_oc) / [contents](#contents) / [class](#class) ]

### to_dict
Returns a `dict` representation of the instance which can be printed / converted
or converted to json. Can be turned back into an instance by passing it to
[from_dict](#instancefrom_dict)

```python
import memory

# Load a session
session = memory.load(somekey)

# Print to console
print(session.to_dict())
```

[ [top](#memory_oc) / [contents](#contents) / [class](#class) ]

### ttl
Getter / Setter for the TTL on the session.

Set
```python
import memory

# Load session
session = memory.load(somekey)

# Returns the current ttl
session.ttl()

# Updates the ttl to 5 minutes and refreshes the session
session.ttl(300)
```

[ [top](#memory_oc) / [contents](#contents) / [class](#class) ]

### update
Works the same as dict update() so you can store multiple keys at once

```python
import memory

# Load session
session = memory.load(somekey)

# Update multiple fields
session.update({
	'name': 'Samuel',
	'phone': '(555) 123-4567'
})

# Save changes
session.save()
```

[ [top](#memory_oc) / [contents](#contents) / [class](#class) ]