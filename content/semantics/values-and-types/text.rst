Text
====

Modern Data supports exactly one text encoding, which is UTF-8, as defined by RFC 3629. Because this encoding is inherently variable-length even with a fixed number of characters, no attempt is made to constrain its size at the level of primitives. Instead, it is treated by Modern Data as a variable-length object.

It would be possible to have a taxonomy of text encodings and character sets, with primitives for conversion. However, the primary goal of Modern Data is to be an interchange format. It is not helpful to authors to have to support many encodings, especially now that UTF-8 is adequate for almost all purposes. Furthermore, custom formats can still be defined in principle by specifying predicates to be satisfied by binary large objects.
