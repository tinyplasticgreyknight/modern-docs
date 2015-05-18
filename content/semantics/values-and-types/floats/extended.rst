80-bit and 128-bit Values
=========================

It is worth noting that, while many platforms support 128-bit float values, many others do not. Even when the compiler does, often the system library does not. This is, not least, because there are no standardized names for the functions - though GNU libquadmath uses the "q" suffix on the ISO C99 base names. The C type which would be the most likely candidate to be a 128-bit float, long double, is actually an 80-bit float on most Intel-related platforms, while non-Intel platforms seldom support anything longer than 64-bit floats.

This creates a situation where there is no one agreed-upon format for very large floating-point numbers, and it is a significant portability burden to write code which uses either, let alone both. Modern Data's purpose is to be an interchange format and lingua franca; therefore, it leaves out support for these types entirely. It is expected that, should a standard emerge, Modern Data will be duly extended in some future revision.

This decision was not made casually; in fact, an early version of the design featured a 128-bit float. The only way to reconcile this design decision with the portability constraints Modern Data aspires to was to use the largest available floating-point type on any given platform for all function parameters and return values, while converting these to and from 128-bit representations for interchange. This was actually implemented at one point, but was removed for the above reasons. A type which cannot be used is - axiomatically! - of no use to anyone.
