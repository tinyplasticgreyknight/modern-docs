Why sigma?
==========

An early version of Modern Data featured separate primitives for structures (also called records), arrays, and unions. A point in favor of this approach is that it makes the job of graphical editors easier, because they don't need to do special logic to determine "this value is an array", for example. However, it was unclear how to fit dependency into this scheme. Adding a dependent pair type solves this problem but makes the other types redundant, and because the other types can all be built out of dependent pairs as well, the editor's task is actually still just as hard. So the decision was made to drop the other types and just build in terms of the dependent pair, which, to give it greater prominence, was given its alternate name of "sigma".
