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
  - [close](#memory-close)
  - [create](#memory-create)
  - [load](#memory-load)
- [Class](#class)
  - [close](#instance-close)
  - [extend](#instance-extend)
  - [key](#instance-key)
  - [save](#instance-save)
  - [update](#instance-update)

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
Memory comes with three methods, to [`close`](#close), [`create`](#create), and  [`load`](#load) sessions.

### close
Immediately closes and deletes a session from Redis.

#### example
```python
import memory

# Closes the session by key
memory.close(somekey)
```

### create
Creates a new session. Takes 3 optional arguments

| Argument | Type | Description |
| -------- | ---- | ----------- |
| `key` | str | The key to use to create the session in Redis. |
| `ttl` | unsigned integer | The time to live in seconds for the session. |
| `data` | dict | The initial data to be stored in the session. |

#### example
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

### load
Loads a session from a passed key.

#### example
```python
import memory

# Loads the session data from Redis
session = memory.load(somekey)

# Change data
session['name'] = 'Samuel'

# Store it in Redis
session.save()
```

[ [top](#memory_oc) / [contents](#contents) ]

## Class
The class is what is returned from the [create](#create) and
[load](#load) methods.

### instance.close
Closes the session in Redis, making it no longer available to anyone.

#### example
```python
import memory

# Load the session
session = memory.load(somekey)

# Close the session
session.close()
```

### instance.extend
Extends the TTL of the session by the initial TTL given.

#### exmaple
```python
import memory

# Load the session
session = memory.load(somekey)

# Extend the session
session.extend()
```

### instance.key
Returns the key of the session.

#### example
```python
import memory

# Create the session
session = memory.create()

# Print the key
print(session.key())
```

### instance.save
Stores changes in Redis after updates.

#### example
```python
import memory

# Load a session
session = memory.load(somekey)

# Make changes
session['name'] = 'Samuel'

# Save changes
session.save()
```

### instance.update
Works the same as dict update() so you can store multiple keys at once

#### example
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

[ [top](#memory_oc) / [contents](#contents) ]