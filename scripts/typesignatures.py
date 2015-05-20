import verify

AP_TYPES = {}

def mktype(ntype, refs):
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
		return TypeWithNames(ntype, refs)
	else:
		raise TypeError("didn't recognise type %s (%s)" % (repr(ntype), type(ntype)))

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
		self.func_name = "(*)"
		self.read_yaml(yaml, refs)

	def read_yaml(self, yaml, refs):
		for term in yaml:
			assert(len(term) == 1)
			pname = list(term.keys())[0]
			ptype = term[pname]
			refs.append(pname)
			param = NamedParam(pname, ptype, refs=refs)
			self.terms.append(param)
			if pname == "result":
				self.result = param.type
			else:
				self.params.append(param)
		if self.result is None:
			rparam = self.params.pop()
			self.result = rparam.type

class ApType(object):
	def __init__(self, inner_type, refs):
		self.ap_name = None
		self.inner_type = mktype(inner_type, refs)

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
		ApType.__init__(self, inner_type, refs)
		self.ap_name = "ptr"
AP_TYPES['ptr'] = PointerType

class FunctionPointerType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs)
		self.ap_name = "funcptr"
AP_TYPES['funcptr'] = FunctionPointerType

class StructType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs)
		self.ap_name = "struct"
AP_TYPES['struct'] = StructType

class EnumType(ApType):
	def __init__(self, inner_type, refs):
		ApType.__init__(self, inner_type, refs)
		self.ap_name = "enum"
AP_TYPES['enum'] = EnumType

class ApTypeNary(ApType):
	def __init__(self, inner_types, refs):
		self.inner_types = [mktype(item, refs) for item in inner_types]
		self.ap_name = None

class SatisfiesType(ApTypeNary):
	def __init__(self, inner_types, refs):
		ApTypeNary.__init__(self, inner_types, refs)
		self.ap_name = "satisfies"
AP_TYPES['satisfies'] = SatisfiesType

class NamedType(ApTypeNary):
	def __init__(self, inner_types, refs):
		ApTypeNary.__init__(self, inner_types, refs)
		self.ap_name = "named"
AP_TYPES['named'] = NamedType

class SigmaType(ApTypeNary):
	def __init__(self, inner_types, refs):
		ApTypeNary.__init__(self, inner_types, refs)
		self.ap_name = "sigma"
AP_TYPES['sigma'] = SigmaType

def format_term_haskell(term):
	return format_haskell_type(term.type, parent="lambda")

def format_join_haskell(func_name, params, result):
	return " -> ".join(params + [result])

def format_component_haskell(signature, here, parent):
	if parent=="top":
		return signature
	if parent=="lambda" and here=="ap":
		return signature
	else:
		return "(%s)" % signature

def format_type(typ, term_formatter, join_formatter, component_formatter, parent="top"):
	def subformat(t, parent):
		return format_type(t, term_formatter, join_formatter, component_formatter, parent=parent)
	if typ is None:
		return "NONE"
	elif type(typ) == str:
		return typ
	elif isinstance(typ, ApType):
		if isinstance(typ, ApTypeNary):
			interior = " ".join([subformat(t, "ap") for t in typ.inner_types])
		elif isinstance(typ, PointerType):
			interior = subformat(typ.inner_type, "top")
			return "%s *" % interior
		else:
			interior = subformat(typ.inner_type, "ap")
		signature = "%s %s" % (typ.ap_name, interior)
		if signature == "maybe universe 0":
			print(parent)
			raise Exception()
		return component_formatter(signature, "ap", parent)
	else:
		result = subformat(typ.result, "lambda")
		vparams = [term_formatter(param) for param in typ.params]
		signature = join_formatter(typ.func_name, vparams, result)
		return component_formatter(signature, "lambda", parent)

def format_visual_type(typ, visual):
	if visual == "haskell":
		return format_haskell_type(typ)
	elif visual == "C":
		return format_C_type(typ)
	else:
		raise KeyError("bad visual %s" % visual)

def format_haskell_type(typ, parent="top"):
	return format_type(typ, format_term_haskell, format_join_haskell, format_component_haskell, parent)

def format_C_type(typ, parent="top"):
	return format_type(typ, format_term_C, format_join_C, format_component_C, parent)

def format_term_C(term):
	type_part = format_C_type(term.type, parent="lambda")
	return "%s %s" % (type_part, term.name)

def format_join_C(func_name, params, result):
	param_str = ", ".join(params)
	return "%s %s(%s)" % (result, func_name, param_str)

def format_component_C(signature, here, parent):
	if parent=="top":
		return signature
	if parent=="lambda" and here=="ap":
		return signature
	else:
		return "(%s)" % signature

def __format_C_type(typ, parent="top"):
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
