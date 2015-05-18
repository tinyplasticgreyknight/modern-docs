Builtin Values
==============

"Built-in value" is a special node type, which consists of an identifier from a sixteen-bit unsigned number-space. Each permitted identifier has a name and a semantic meaning, described in this section. Unlike most other node types, the value type of a built-in value depends (solely) on its identifier. Thus, this node type could be viewed as an "extension" node type, providing a larger number-space.

Many of the extant built-in values exist to provide primitive operations on the other value types, such as arithmetic, trigonometry, and introspection. There is also one, if_bool , which provides flow control. Because loops can be implemented with cyclic structures (which is to say, with let-bindings), no other flow-control constructs are necessary to be Turing-complete.

The reader is urged not to inspect the ordering of the symbols within the number-space too carefully, as it will reveal embarrassing details of the order in which concepts were invented during early drafts of Modern Data! They are presented in this document in a logical order and grouping; the actual numbers assignations are purely an implementation detail.

The human-readable names, numeric values, and semantics are given, in order to attain some approximation of brevity, in a top-level section of this document, Builtin identifiers, alongside the C-library names.
