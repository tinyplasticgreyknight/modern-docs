import verify

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
