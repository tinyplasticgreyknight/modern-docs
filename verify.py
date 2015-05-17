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
