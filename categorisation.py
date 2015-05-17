import os
import io
from funcs import *
from verify import *

AP_TYPES = {}

def mktype(ntype, refs):
	if type(ntype) == str or type(ntype) == int:
		verify_type(str(ntype), refs)
		return str(ntype)
	elif type(ntype) == dict:
		apkeys = AP_TYPES.keys()
		for ctor_name in apkeys:
			if ctor_name in ntype:
				ctor = AP_TYPES[ctor_name]
				return ctor(ntype[ctor_name], refs)
		raise TypeError("didn't recognise ap-type %s" % repr(ntype))
	elif type(ntype) == list:
		return TypeWithNames(ntype, refs)
	else:
		raise TypeError("didn't recognise type %s (%s)" % (repr(ntype), type(ntype)))

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
	def __init__(self, name, ntype, refs=None):
		if refs is None: refs = []
		self.name = name
		self.type = mktype(ntype, refs)

class TypeWithNames(object):
	def __init__(self, yaml, refs=None):
		if refs is None: refs = []
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
			if (type(ttyp) == str) or isinstance(ttyp, ApType):
				vterms.append(str(ttyp))
			else:
				vterms.append("(%s)" % str(ttyp))
		return " -> ".join(vterms)

class ApType(object):
	def __init__(self, inner_type, refs):
		self.ap_name = None
		self.inner_type = mktype(inner_type, refs)

	def str_interior_part(self, obj):
		if type(obj) == str:
			return obj
		else:
			return "(%s)" % str(obj)

	def interior(self):
		return self.str_interior_part(self.inner_type)

	def __str__(self):
		return "%s %s" % (self.ap_name, self.interior())

class MaybeType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs)
		self.ap_name = "maybe"
AP_TYPES['maybe'] = MaybeType

class UniverseType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs)
		self.ap_name = "universe"
AP_TYPES['universe'] = UniverseType

class ApType2ary(ApType):
	def __init__(self, inner_types, refs):
		assert(len(inner_types) == 2)
		self.inner0 = mktype(inner_types[0], refs)
		self.inner1 = mktype(inner_types[1], refs)
		self.ap_name = None

	def interior(self):
		return "%s %s" % (self.str_interior_part(self.inner0), self.str_interior_part(self.inner1))

class SatisfiesType(ApType2ary):
	def __init__(self, inner_types, refs):
		ApType2ary.__init__(self, inner_types, refs)
		self.ap_name = "satisfies"
AP_TYPES['satisfies'] = SatisfiesType

class NamedType(ApType2ary):
	def __init__(self, inner_types, refs):
		ApType2ary.__init__(self, inner_types, refs)
		self.ap_name = "named"
AP_TYPES['named'] = NamedType

class SigmaType(ApType2ary):
	def __init__(self, inner_types, refs):
		ApType2ary.__init__(self, inner_types, refs)
		self.ap_name = "sigma"
AP_TYPES['sigma'] = SigmaType

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
