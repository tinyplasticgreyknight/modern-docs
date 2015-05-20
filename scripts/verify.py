import re

PRIMITIVE_TYPES = [
	"bool",
	"int8",
	"int16",
	"int32",
	"int64",
	"nat8",
	"nat16",
	"nat32",
	"nat64",
	"float32",
	"float64",
	"name",
	"ordering",
	"blob",
	"utf8",
	"[0-9]+",
]

C_PRIMITIVE_TYPES = [
	"void",
	"int",
	"float",
	"double",
	"char",
]

C_INCLUDED_TYPES = [
	"size_t",
	"ssize_t",
	"int8_t",
	"int16_t",
	"int32_t",
	"int64_t",
	"uint8_t",
	"uint16_t",
	"uint32_t",
	"uint64_t",
	"FILE",
]

# TODO: probably these can be loaded from modern.h
C_LIBRARY_TYPES = [
	"modern",
	"modern_library",
	"modern_error_handler",
	"modern_allocator",
	"modern_node_representation",
	"modern_node_type",
	"modern_hash",
	"modern_stream",
	"modern_vfile",
	"modern_process",
]

PERMITTED_TYPES = []

for tlist in [PRIMITIVE_TYPES, C_PRIMITIVE_TYPES, C_INCLUDED_TYPES, C_LIBRARY_TYPES]:
	for name in tlist:
		PERMITTED_TYPES.append(re.compile("^%s$" % name))

def types(supposed, refs):
	for pattern in PERMITTED_TYPES:
		if pattern.match(supposed):
			return True
	if supposed in refs:
		return True
	raise TypeError("did not recognise %s as a type" % repr(supposed))

def consistency(cat):
	def _verify_ident(leaf, idents):
		if leaf.ident is None: return
		existing = idents.get(leaf.ident)
		if existing is None: return
		raise KeyError("ident %d is assigned to both %s and %s" % (leaf.ident, existing.name, leaf.name))
	def _verify_name(leaf, leaf_names):
		if leaf.name is None: return
		if leaf.ident is None: return
		existing = leaf_names.get(leaf.name)
		if existing is None: return
		raise KeyError("name %s is assigned to more than one thing" % leaf.name)

	def _verify(cat, idents, leaf_names):
		for leaf in cat.leaves:
			_verify_ident(leaf, idents)
			_verify_name(leaf, leaf_names)
			idents[leaf.ident] = leaf
			leaf_names[leaf.name] = leaf

		for child in cat.children:
			_verify(child, idents, leaf_names)
	_verify(cat, {}, {})
