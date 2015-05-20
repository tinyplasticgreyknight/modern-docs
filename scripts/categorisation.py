import os
import io
import directory
import verify
from write_rest import *

AP_TYPES = {}

def mktype(ntype, refs, visual="haskell"):
	if type(ntype) == str or type(ntype) == int:
		verify.type_name(str(ntype), refs)
		return str(ntype)
	elif type(ntype) == dict:
		apkeys = AP_TYPES.keys()
		for ctor_name in apkeys:
			if ctor_name in ntype:
				ctor = AP_TYPES[ctor_name]
				return ctor(ntype[ctor_name], refs)
		raise TypeError("didn't recognise ap-type %s" % repr(ntype))
	elif type(ntype) == list:
		if visual == "haskell":
			return TypeWithNames(ntype, refs)
		elif visual == "C":
			typ = CTypeWithNames(ntype, refs)
			return typ
	else:
		raise TypeError("didn't recognise type %s (%s)" % (repr(ntype), type(ntype)))

class Leaf(object):
	def __init__(self, ident, name, semantics=None):
		self.ident = ident
		self.name = name
		self.semantics = semantics
		self.level = 0

	def create_entry(self, path_prefix):
		filename = os.path.join(path_prefix, "%s.rst" % self.name)
		with io.open(filename, 'w') as stream:
			self.write_entry(stream)

	def write_entry(self, stream):
		write_rest_header(stream, self.name, self.level)
		write_rest_header(stream, "Synopsis", self.level+1)
		self.write_synopsis(stream)
		self.write_entry_extra(stream)
		if self.semantics is not None:
			stream.write("\n")
			write_rest_header(stream, "Semantics", self.level+1)
			self.write_semantics(stream)

	def write_entry_extra(self, stream):
		pass

	def write_synopsis(self, stream):
		stream.write("* **Numeric value:** %d\n" % self.ident)
		stream.write("* **Standard name:** ``%s``\n" % self.name)

	def write_semantics(self, stream):
		stream.write("%s\n" % self.semantics)

class NamedParam(object):
	def __init__(self, name, ntype, refs=None, visual="haskell"):
		if refs is None: refs = []
		self.name = name
		self.type = mktype(ntype, refs, visual)

class TypeWithNames(object):
	def __init__(self, yaml, refs=None, visual="haskell"):
		if refs is None: refs = []
		self.terms = []
		self.params = []
		self.result = None
		self.read_yaml(yaml, refs, visual)

	def read_yaml(self, yaml, refs, visual):
		for term in yaml:
			assert(len(term) == 1)
			name = list(term.keys())[0]
			ptype = term[name]
			refs.append(name)
			param = NamedParam(name, ptype, refs=refs, visual=visual)
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

class CTypeWithNames(TypeWithNames):
	def __init__(self, yaml, refs=None, visual="C"):
		TypeWithNames.__init__(self, yaml, refs, visual)
		self.func_name = "(*)"

	def __str__(self):
		if len(self.params) == 0:
			return str(self.result)
		vterms = []
		for term in self.params:
			ttyp = term.type
			if (type(ttyp) == str) or isinstance(ttyp, ApType):
				vterms.append("%s %s" % (str(ttyp), term.name))
			else:
				vterms.append("(%s)" % str(ttyp))
		param_str = ", ".join(vterms)
		return "%s %s(%s)" % (str(self.result), self.func_name, param_str)

class ApType(object):
	def __init__(self, inner_type, refs, visual="haskell"):
		self.ap_name = None
		self.inner_type = mktype(inner_type, refs, visual)

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

class PointerType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs, visual="C")
		self.ap_name = "ptr"

	def __str__(self):
		return "%s *" % self.inner_type
AP_TYPES['ptr'] = PointerType

class FunctionPointerType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs, visual="C")
		self.ap_name = "funcptr"

	def __str__(self):
		return str(self.inner_type)
AP_TYPES['funcptr'] = FunctionPointerType

class StructType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs, visual="C")
		self.ap_name = "struct"
AP_TYPES['struct'] = StructType

class EnumType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs, visual="C")
		self.ap_name = "enum"
AP_TYPES['enum'] = EnumType

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
	def __init__(self, ntype=None, fixed_value=None, *args, **kwargs):
		Leaf.__init__(self, *args, **kwargs)
		self.type = None
		self.fixed_value = fixed_value
		if ntype is not None:
			self.type = TypeWithNames(ntype)

	def write_entry_extra(self, stream):
		if self.type is None:
			return
		stream.write("* **Type:** ``%s``\n" % str(self.type))
		if len(self.type.params) > 0:
			stream.write("* **Parameters:**\n\n")
			for param in self.type.params:
				stream.write("  - *%s* : ``%s``\n" % (param.name, str(param.type)))
			stream.write("\n")
			stream.write("* **Result:** ``%s``\n" % str(self.type.result))
		if self.fixed_value is not None:
			stream.write("* **Fixed Value:** ``%s``\n" % str(self.fixed_value))

class CCommon(Builtin):
	def __init__(self, name, *args, **kwargs):
		Builtin.__init__(self, ident=None, name=name, ntype=None, *args, **kwargs)

	def set_type(self, ntype):
		self.type = ntype

	def write_synopsis(self, stream):
		stream.write("* **Name:** ``%s``\n" % self.name)

class CFunction(CCommon):
	def __init__(self, *args, **kwargs):
		CCommon.__init__(self, *args, **kwargs)

	def set_type(self, ntype):
		CCommon.set_type(self, ntype)
		self.type.func_name = self.name

class CStructField(CCommon):
	def __init__(self, struct_name, *args, **kwargs):
		CCommon.__init__(self, *args, **kwargs)
		self.struct_name = struct_name
		self.level += 1

	def write_entry(self, stream):
		stream.write("\n")
		write_rest_header(stream, self.name, self.level)
		self.write_synopsis(stream)
		self.write_entry_extra(stream)
		if self.semantics is not None:
			self.write_semantics(stream)

class Category(object):
	def __init__(self, title, name=None, toc_depth=1, is_root=False, use_intro=None):
		self.title = title
		self.name = name
		self.toc_depth = toc_depth
		self.is_root = is_root
		self.has_own_header = False
		self.print_toc_as_struct = False
		self.children = []
		self.leaves = []
		self.intro_text = None
		self.contents = None
		self.child_ordering = None
		if use_intro is not None:
			with io.open(use_intro, 'r') as f:
				self.intro_text = f.read()

	def add_child(self, child):
		self.children.append(child)

	def add_leaf(self, leaf):
		self.leaves.append(leaf)

	def toc_entry(self):
		return "%s/index" % self.name

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
		dirname = self.dirname(path_prefix)
		directory.ensure_exists(dirname)
		with io.open(os.path.join(dirname, "index.rst"), 'w') as f:
			write_index(f, self)

	def ordered_children(self):
		if self.child_ordering is None: return self.children.copy()
		ordered = []
		not_seen = set(self.children)
		by_name = {}
		for child in self.children:
			by_name[child.name] = child

		for name in self.child_ordering:
			child = by_name[name]
			not_seen.discard(child)
			ordered.append(child)

		if len(not_seen) > 0:
			raise KeyError("some children were not included in the ordering: %s" % [x.name for x in not_seen])

		return ordered

class RawChunk(Category):
	def __init__(self, filename, name):
		Category.__init__(self, name, name)
		self.name = name
		self.title = name
		self.toc_depth = 0
		self.has_own_header = True
		with io.open(filename, 'r') as f:
			self.contents = f.read()

	def create_tree(self, path_prefix):
		dirname = self.dirname(path_prefix)
		directory.ensure_exists(os.path.dirname(dirname))
		filename = dirname + ".rst"

		with io.open(filename, 'w') as f:
			write_index(f, self)

	def toc_entry(self):
		return self.name

class CStructCategory(Category):
	def __init__(self, title, name, refs=None, visual="C"):
		Category.__init__(self, title, name, toc_depth=1)
		self.print_toc_as_struct = True

	def create_tree(self, path_prefix):
		dirname = self.dirname(path_prefix)
		directory.ensure_exists(os.path.dirname(dirname))
		filename = dirname + ".rst"

		with io.open(filename, 'w') as f:
			write_index(f, self)
			for leaf in self.leaves:
				leaf.write_entry(f)

	def toc_entry(self):
		return self.name
