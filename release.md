# memory_oc releases

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