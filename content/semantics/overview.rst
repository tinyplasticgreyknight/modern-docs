Overview
========

In Modern Data, the fundamental in-memory datatype is the "modern node", which is a representation of, loosely, either a value or a type. If we wish to specify further, we may occasionally refer to a "modern type" or "modern value", but these concepts do not map to actual host-language datatypes; only "modern node" does.

The operations on a modern node are serialization, deserialization, type-checking, evaluation, and traversal. The concept of a "modern context" holding types and values is used by serialization, deserialization, type-checking, and evaluation. The concept of a "modern cursor" describing a node and a path to reach it from the root is used by traversal.

Serialization is performed on a modern node in some modern context, and produces a stream of bytes.

Deserialization is performed on a stream of bytes in some modern context, and produces a modern node.

Evaluation is performed on a modern node, and produces another modern node. Traversal is begun by creating a "modern cursor" from some modern node

Although simple applications which merely wish to exchange and act on data need never use anything but the default context, it is nonetheless a concept worth understanding. The context is internally a hash table of modern types (and occasionally modern values, used as parts of dependent types). The hash key is determined in a way that captures the notion of type equality, by placing the modern node in a canonical form and computing a hash function of that. Any modern node which is in the hash table is "in scope" in that context.
