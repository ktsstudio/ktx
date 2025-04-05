# 0.4.0
Breaking changes:
* rename `Context` protocol to `AbstractContext`
* renamed `SimpleContext` to `Context`
* removed `SimpleContext.data` property
* removed `get_user()` from `Context` and `SimpleContext`
* rename term `wrap` to `bind` and attach/detach to bind/unbind
* removed `SimpleContextData` class
* `ktx_id` is now required to create `Context`
* `ktx_add_log` now does not add user info as there's now no user info in the context

New features:
* Introduced new `AbstractContextUser` protocol with `ContextUser` implementation to hold user info
* Added abstract adapter ability to include in the Context and ContextUser properties' setting
* Introduced `ContextFactory` and `ContextUserFactory` to create Context and ContextUser with the ability to modify creation behaviour.
* New `ktx_add_user_log` to add user info to log's event dict

# 0.3.0
* rename uq_id to ktx_id
* remove opentelemetry dependency

# 0.2.3
* move to github
* change license to Apache 2.0

# 0.2.2
* remove opentelemetry-sdk from dependencies

# 0.2.1
* add `ctx` property to `ContextWrap`

# 0.2.0
* simplify context - it is not longer a Generic class/Protocol
* added ctx_wrap function that attached context to ContextVar
* removed GenericContext

# 0.1.4
* log: serialize data fields and user id always as str

# 0.1.3
* fix tests
* support for python >= 3.9

# 0.1.2
* flat dict in logging

# 0.1.0

* Initial release
