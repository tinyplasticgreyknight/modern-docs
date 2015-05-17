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

for i in range(len(PRIMITIVE_TYPES)):
	PRIMITIVE_TYPES[i] = re.compile("^%s$" % PRIMITIVE_TYPES[i])

def verify_type(supposed, refs):
	for pattern in PRIMITIVE_TYPES:
		if pattern.match(supposed):
			return True
	if supposed in refs:
		return True
	raise TypeError("did not recognise %s as a type" % repr(supposed))

def verify_consistency(cat):
	def _verify_ident(leaf, idents):
		if leaf.ident is None: return
		existing = idents.get(leaf.ident)
		if existing is None: return
		raise KeyError("ident %d is assigned to both %s and %s" % (leaf.ident, existing.name, leaf.name))
	def _verify_name(leaf, leaf_names):
		if leaf.name is None: return
		existing = leaf_names.get(leaf.name)
		if existing is None: return
		raise KeyError("name %s is assigned to both %d and %d" % str(leaf.name), existing.ident, leaf.ident)

	def _verify(cat, idents, leaf_names):
		for leaf in cat.leaves:
			_verify_ident(leaf, idents)
			_verify_name(leaf, leaf_names)
			idents[leaf.ident] = leaf
			leaf_names[leaf.name] = leaf

		for child in cat.children:
			_verify(child, idents, leaf_names)
	_verify(cat, {}, {})
