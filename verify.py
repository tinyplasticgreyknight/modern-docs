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
	raise TypeError("did not recognise %s as a primitive type" % repr(supposed))

def verify_consistency(cat):
	def _verify(cat, idents):
		for leaf in cat.leaves:
			existing = idents.get(leaf.ident)
			if existing is not None:
				raise KeyError("ident %d is assigned to both %s and %s" % (leaf.ident, existing.name, leaf.name))
			idents[leaf.ident] = leaf
		for child in cat.children:
			_verify(child, idents)
	_verify(cat, {})
