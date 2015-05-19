import io
import pycparser
from categorisation import CFunction, CStructField, CTypeWithNames, FunctionPointerType

FAKE_TYPES = [
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

def parse_library_header(filename):
	parser = pycparser.CParser()
	with io.open(filename, 'r') as f:
		text = ""
		for fake_type in FAKE_TYPES:
			text += "typedef void %s;" % fake_type
		for line in f:
			if (line != "") and (line[0] != '#'): break
		return parser.parse(text + f.read(), filename)

def apply_types_for_c(category, ast):
	for leaf in category.leaves:
		if isinstance(leaf, CFunction):
			apply_func_type(leaf, ast)
		elif isinstance(leaf, CStructField):
			apply_field_type(leaf, ast)
	for child in category.children:
		apply_types_for_c(child, ast)

def apply_func_type(cleaf, ast):
	node = find_func_decl(cleaf.name, ast)
	if node is None:
		raise KeyError("cannot find function %s" % cleaf.name)
	sig = signature(node)
	cleaf.set_type(CTypeWithNames(sig))

def apply_field_type(cleaf, ast):
	cleaf.set_type(CTypeWithNames([{'result': "void"}]))

def find_func_decl(name, root):
	for _child in root.children():
		child = _child[1]
		if not isinstance(child, pycparser.c_ast.Decl): continue
		if child.name == name: return child
	raise KeyError("function %s not found" % name)

def get_child(decl, kind):
	coll = []
	for child_pair in decl.children():
		coll.append(child_pair[0])
		if child_pair[0] == kind:
			child = child_pair[1]
			return child
	raise KeyError("cannot find %s in %s" % (kind, coll))

def signature(decl):
	if isinstance(decl, pycparser.c_ast.FuncDecl):
		return signature_func(decl)
	if isinstance(decl, pycparser.c_ast.PtrDecl):
		return signature_pointer(decl)
	if isinstance(decl, pycparser.c_ast.Struct):
		return {'struct': decl.name}
	if isinstance(decl, pycparser.c_ast.IdentifierType):
		return " ".join(decl.names)
	if len(decl.children()) == 0:
		raise IndexError()
	return signature(get_child(decl, 'type'))

def signature_func(decl):
	ftype = []
	param_list = get_child(decl, 'args')
	return_type = get_child(decl, 'type')
	tret = type(return_type)
	assert(isinstance(param_list, pycparser.c_ast.ParamList))
	assert(tret in [pycparser.c_ast.TypeDecl, pycparser.c_ast.PtrDecl])
	for _param in param_list.children():
		param = _param[1]
		pname = param.name
		ptype = signature(get_child(param, 'type'))
		ftype.append({pname: ptype})
	ftype.append({'result': signature(return_type)})
	return ftype

def signature_pointer(decl):
	child = get_child(decl, 'type')
	if isinstance(child, pycparser.c_ast.TypeDecl):
		child = get_child(child, 'type')
	if isinstance(child, pycparser.c_ast.FuncDecl):
		return {'funcptr': signature(child)}
	else:
		return {'ptr': signature(child)}

def signature_typed_name(decl):
	return {decl.declname: signature(get_child(decl, 'type'))}
