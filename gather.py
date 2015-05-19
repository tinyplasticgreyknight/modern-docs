import os
import io
import yaml
from categorisation import *

def gather_directory(title, path_prefix, dirname, gather_leaf=None, mask=None):
	cat = Category(title=title, name=dirname)
	scan_path = os.path.join(path_prefix, dirname)
	if (mask is not None):
		if os.path.normpath(scan_path) in mask:
			print("masked: %s" % scan_path)
			return cat
	if gather_leaf is None:
		if dirname == "builtins":
			gather_leaf = gather_yaml_builtin
		elif dirname == "nodes":
			gather_leaf = gather_yaml_node
		elif dirname == "c-library":
			gather_leaf = gather_yaml_c
	for entry in os.listdir(scan_path):
		gather_directory_entry(cat, scan_path, entry, gather_leaf, mask)
	return cat

def gather_directory_entry(cat, scan_path, entry, gather_leaf, mask):
	full_entry = os.path.join(scan_path, entry)
	if os.path.isdir(full_entry):
		child_dirname = os.path.basename(entry)
		subdir = gather_directory(entry, scan_path, child_dirname, gather_leaf, mask=mask)
		cat.add_child(subdir)
	elif os.path.isfile(full_entry):
		suffix = os.path.splitext(entry)[1]
		if entry == '_meta.yaml':
			load_metadata(cat, full_entry)
		elif entry == 'index.rst':
			with io.open(full_entry, 'r') as f:
				cat.intro_text = f.read()
		elif suffix == '.yaml':
			cat.add_child(gather_yaml_category(full_entry, gather_leaf))
		elif suffix == '.rst':
			cat.add_child(RawChunk(full_entry, file_name_token(entry)))

def load_metadata(category, meta_filename):
	with io.open(meta_filename, 'r') as f:
		meta = yaml.load(f)
		category.title = meta.get('title', category.title)
		category.child_ordering = meta.get('order', category.child_ordering)

def file_name_token(filename):
	return os.path.splitext(os.path.basename(filename))[0]

def gather_yaml_category(yamlfile, gather_leaf):
	with io.open(yamlfile, 'r') as f:
		doc = yaml.load(f)
		name = doc.get('name', file_name_token(yamlfile))
		title = doc['title']
		struct_name = doc.get('documents-struct')
		cat = None
		if struct_name is not None:
			cat = CStructCategory(title=title, name=struct_name)
			gather_leaf = gather_yaml_c_structfield
			extra = struct_name
		else:
			cat = Category(title=title, name=name)
			extra = None
		for leaf in doc['entries']:
			cat.add_leaf(gather_leaf(leaf, extra))
		return cat

def gather_yaml_node(yaml, _):
	leaf = Leaf(ident=yaml['id'], name=yaml['name'], semantics=yaml.get('semantics'))
	return leaf

def gather_yaml_builtin(yaml, _):
	leaf = Builtin(ident=yaml['id'], name=yaml['name'], semantics=yaml.get('semantics'), ntype=yaml.get('type'), fixed_value=yaml.get('fixed-value'))
	return leaf

def gather_yaml_c(yaml, _):
	return gather_yaml_c_func(yaml, _)

def gather_yaml_c_func(yaml, _):
	leaf = CFunction(name=yaml['name'], semantics=yaml.get('semantics'))
	return leaf

def gather_yaml_c_structfield(yaml, struct_name):
	leaf = CStructField(name=yaml['name'], struct_name=struct_name, semantics=yaml.get('semantics'))
	return leaf
