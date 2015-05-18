Scoping
=======

Importantly, a modern type must be in scope in the given context before a value of that type can be serialized or deserialized. The high-level "node-based" portion of the library will check whether a value's type is in context when serializing, and emit additional instructions which bring it into context if it is not, mutating the context object which it is passed to make note of the fact. Similarly, when deserializing, if a value's type is not in context, an error is produced and processing halts. (To avoid security holes caused by different implementations responding to errors in different ways, processing is specified to always halt immediately upon the first error encountered.)

The low-level "stream-based" portion of the library does no such checking, as it tracks very little internal state, leaving that task to the client code. The client code is thus responsible for ensuring that types are in context before they are used, both when serializing and when deserializing.
