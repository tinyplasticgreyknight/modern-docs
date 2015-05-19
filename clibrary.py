import io
import pycparser
from categorisation import CFunction, CStructField, CStructCategory, CTypeWithNames, FunctionPointerType
from verify import C_INCLUDED_TYPES

def parse_library_header(filename):
	parser = pycparser.CParser()
	with io.open(filename, 'r') as f:
		text = ""
		for fake_type in C_INCLUDED_TYPES:
			if fake_type == "void": continue
			text += "typedef void %s;" % fake_type
		for line in f:
			if (line != "") and (line[0] != '#'): break
		return parser.parse(text + f.read(), filename)

def apply_types_for_c(category, ast):
	for leaf in category.leaves:
		if isinstance(leaf, CFunction):
			apply_func_type(leaf, ast)
		elif isinstance(leaf, CStructField):
			print(category)
			raise Exception("Not possible!")
	for child in category.children:
		if isinstance(child, CStructCategory):
			apply_struct_types(child, ast)
		else:
			apply_types_for_c(child, ast)

def apply_func_type(leaf, ast):
	node = find_func_decl(leaf.name, ast)
	if node is None:
		raise KeyError("cannot find declaration for function %s in header" % leaf.name)
	sig = signature(node)
	leaf.set_type(CTypeWithNames(sig))

def apply_struct_types(cat, ast):
	node = find_struct_decl(cat.name, ast)
	if node is None:
		raise KeyError("cannot find definition for struct %s in header" % cat.name)
	for leaf in cat.leaves:
		if not isinstance(leaf, CStructField):
			raise SyntaxError("found non-struct-field in struct %s: %s" % (cat.name, str(leaf)))
		apply_field_type(cat, leaf, node)

def apply_field_type(cat, leaf, struct_ast):
	node = find_field_decl(cat.name, leaf.name, struct_ast)
	if node is None:
		raise KeyError("cannot find definition for struct field %s.%s in header" % (cat.name, leaf.name))
	sig = signature(node)
	#sig = sig # TODO: probably need to fix up signature() to resolve this properly
	leaf.set_type(CTypeWithNames(sig))

def find_func_decl(name, root):
	for _child in root.children():
		child = _child[1]
		if not is_decl_for(child, pycparser.c_ast.FuncDecl): continue
		if child.name == name: return child
	raise KeyError("function %s not found" % name)

def find_struct_decl(name, root):
	for _child in root.children():
		child = _child[1]
		if not is_decl_for(child, pycparser.c_ast.Struct): continue
		grandchild = get_child(child, 'type')
		if grandchild.name == name: return grandchild
	raise KeyError("struct %s not found" % name)

def find_field_decl(struct_name, name, struct):
	for _child in struct.children():
		child = _child[1]
		if not isinstance(child, pycparser.c_ast.Decl): continue
		if child.name == name: return get_child(child, 'type')
	raise KeyError("struct field %s not found" % name)

def is_decl_for(node, decl_type):
	if not isinstance(node, pycparser.c_ast.Decl): return False
	children = node.children()
	if len(children) == 0: return False
	first_child = children[0]
	return first_child[0] == 'type' and isinstance(first_child[1], decl_type)

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
	if isinstance(decl, pycparser.c_ast.Enum):
		return {'enum': decl.name}
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
		return signature(child)
	else:
		return {'ptr': signature(child)}

def signature_typed_name(decl):
	return {decl.declname: signature(get_child(decl, 'type'))}
