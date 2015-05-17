import os
import io
import re
from funcs import *

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
	"universe [0-9]+",
	"name",
	"ordering",
	"blob",
	"utf8",
]

for i in range(len(PRIMITIVE_TYPES)):
	PRIMITIVE_TYPES[i] = re.compile("^%s$" % PRIMITIVE_TYPES[i])

def verify_primitive_type(supposed, refs):
	for pattern in PRIMITIVE_TYPES:
		if pattern.match(supposed):
			return True
	if supposed in refs:
		return True
	raise TypeError("did not recognise %s as a primitive type" % repr(supposed))

def mktype(ntype, refs):
	if type(ntype) == str:
		verify_primitive_type(ntype, refs)
		return ntype
	elif type(ntype) == dict:
		if "maybe" in ntype:
			return MaybeType(ntype['maybe'], refs)
		else:
			raise TypeError("didn't recognise monadic type %s" % repr(ntype))
	elif type(ntype) == list:
		return TypeWithNames(ntype, refs)
	else:
		raise TypeError("didn't recognise type %s" % repr(ntype))

class Leaf(object):
	def __init__(self, ident, name, semantics=None):
		self.ident = ident
		self.name = name
		self.semantics = semantics

	def create_entry(self, path_prefix):
		filename = os.path.join(path_prefix, "%s.rst" % self.name)
		with io.open(filename, 'w') as stream:
			self.write_synopsis(stream)
			self.write_entry(stream)
			self.write_semantics(stream)

	def write_entry(self, stream):
		pass

	def write_synopsis(self, stream):
		write_rest_header(stream, self.name, kind="=")
		write_rest_header(stream, "Synopsis", kind="-")
		stream.write("* **Numeric value:** %d\n" % self.ident)
		stream.write("* **Standard name:** ``%s``\n" % self.name)

	def write_semantics(self, stream):
		if self.semantics is None:
			return
		stream.write("\n")
		write_rest_header(stream, "Semantics", kind="-")
		stream.write("%s\n" % self.semantics)

class NamedParam(object):
	def __init__(self, name, ntype, refs=[]):
		self.name = name
		self.type = mktype(ntype, refs)

class TypeWithNames(object):
	def __init__(self, yaml, refs=[]):
		self.terms = []
		self.params = []
		self.result = None
		for term in yaml:
			assert(len(term) == 1)
			name = list(term.keys())[0]
			ptype = term[name]
			refs.append(name)
			param = NamedParam(name, ptype, refs=refs)
			self.terms.append(param)
			if name == "result":
				self.result = param.type
			else:
				self.params.append(param)

	def __str__(self):
		vterms = []
		for term in self.terms:
			ttyp = term.type
			if (type(ttyp) == str) or (type(ttyp) == MaybeType):
				vterms.append(str(ttyp))
			else:
				vterms.append("(%s)" % str(ttyp))
		return " -> ".join(vterms)

class MaybeType(object):
	def __init__(self, inner_type, refs):
		self.inner_type = mktype(inner_type, refs)

	def __str__(self):
		if type(self.inner_type) == str:
			return "maybe %s" % self.inner_type
		else:
			return "maybe (%s)" % str(self.inner_type)

class Builtin(Leaf):
	def __init__(self, type=None, *args, **kwargs):
		Leaf.__init__(self, *args, **kwargs)
		self.type = TypeWithNames(type)

	def write_entry(self, stream):
		if self.type is None:
			return
		stream.write("* **Type:** ``%s``\n" % str(self.type))
		stream.write("* **Parameters:**\n\n")
		if len(self.type.terms) == 0:
			return
		for param in self.type.params:
			stream.write("  - *%s* : ``%s``\n" % (param.name, str(param.type)))
		stream.write("\n")
		stream.write("* **Result:** ``%s``\n" % str(self.type.result))

class Category(object):
	def __init__(self, title, name=None, toc_depth=1, is_root=False):
		self.title = title
		self.name = name
		self.toc_depth = toc_depth
		self.is_root = is_root
		self.children = []
		self.leaves = []

	def add_child(self, child):
		self.children.append(child)

	def add_leaf(self, leaf):
		self.leaves.append(leaf)

	def create_tree(self, path_prefix):
		self.create_index(path_prefix)
		for child in self.children:
			child.create_tree(self.dirname(path_prefix))
		for leaf in self.leaves:
			leaf.create_entry(self.dirname(path_prefix))

	def dirname(self, path_prefix):
		if self.name is None:
			return path_prefix
		else:
			return os.path.join(path_prefix, self.name)

	def create_index(self, path_prefix):
		directory = self.dirname(path_prefix)
		ensure_dir_exists(directory)
		with io.open(os.path.join(directory, "index.rst"), 'w') as f:
			write_index(f, self)
