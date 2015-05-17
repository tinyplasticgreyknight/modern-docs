The C-based library is a major part of the Modern Data system. It is the foundation for the library in all other languages except JavaScript, due to the ease of linking against and using C. It is designed to allow pieces of the system to be swapped out with ease, not just the allocator but the actual representation of nodes. There is a fair amount of setup that needs to be done in order to use it, so it is recommended to read these overview sections in order.

In order to be considerate about namespace, all symbols that the library exports start with the string ``"modern_"``.
