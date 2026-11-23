# memory_oc releases

## 1.0.5
- Updated strings_oc to 1.0.5 for security fix.
- Added `from_dict` to `__all__`.
- Declared missing `config_oc` and `tools_oc` package dependencies.
- Sessions now persist to Redis automatically on `create` and whenever
  data changes. `save()` is deprecated and emits a `DeprecationWarning`.
- `create` now claims keys with Redis `SET NX` so two creates cannot both
  succeed for the same key.

## 1.0.4
- Added `to_dict()` instance method and `from_dict()` module method to allow
converting back and forth from dicts.

## 1.0.3
- Added `ttl()` instance method to allow getting / setting time to live at
runtime. Setting a new value will immediately update the key's expiry in Redis.

## 1.0.2
- Fixed a bug in `create` where any `key` passed was ignored and instead randomly generated.
- Added top level `close` method so you don't need to load a session in order to close it.
- Added a third option to `create` to allow immediately setting data in the session.
- Added `update` method to `_Memory` so multiple fields can be set at once.
- Added documentation / examples in README.

## 1.0.1
- Switched from memory-oc to memory_oc to satisfy pip.
- Refactored `create()` to generate a random key instead of a UUID which was not very safe.

## 1.0.0
- Initial release.