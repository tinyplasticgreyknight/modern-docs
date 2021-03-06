A library instance is an opaque structure which represents a single configured copy of the system. It is a basic type which, once constructed, is passed to every function. It contains structures of pointers to callbacks which are used to accomplish all the low-level tasks the library needs to conduct. Callback structures are used in several places in the system, and not all of them are part of the library instance - only the most fundamental ones.

In all callbacks, the library is written with the expectation that the client code may ``longjmp()`` or cause program termination at any time, and will not crash upon these events. Allocation failure is also not the unrecoverable condition that it is in some systems; it is permitted, and will cause neither crashes nor memory leaks. The test suite verifies all of these behaviours extensively.

Library instances (as all of Modern Data) are threading-naive; that is, they use no thread-local storage, but also do no internal locking. No special action is needed to migrate a library instance from one operating-system thread to another, but only one thread may be in the midst of a library call at any given moment.

The callback structures are the error handler, the allocator, and the node routines; the client state, an opaque pointer for the use of client code, is also part of the library instance's state. None of these can be changed once the library instance is initialized, but they can be retrieved and inspected at any time.

The most fundamental task is error handling. In order to allow the system to be robust against allocation failure, it is necessary that there be no heap allocation required to process an error! As such, each possible error condition has its own callback. This leads to a verbose style, but is typically what one wants in any event.

The next-most-important task is memory allocation. This is straightforward and does not need further discussion.

The final important task is to handle primitive operations on the representation of nodes. The library provides a default implementation here, but in order to bind more closely with non-C programming languages, the capability to provide one's own is also provided. All access to the internal structures is indirected through these callbacks, with the result that all the basic operations (serialization, evaluation, and so on) can be performed regardless of the actual node representation.
