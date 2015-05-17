import os
import io
import yaml
from categorisation import *

def gather_directory(title, path_prefix, dirname, gather_leaf=None):
	cat = Category(title=title, name=dirname)
	scan_path = os.path.join(path_prefix, dirname)
	if gather_leaf is None:
		if dirname == "builtins":
			gather_leaf = gather_yaml_builtin
		elif dirname == "nodes":
			gather_leaf = gather_yaml_node
	for entry in os.listdir(scan_path):
		full_entry = os.path.join(scan_path, entry)
		if os.path.isdir(full_entry):
			subdir = gather_directory(entry, scan_path, os.path.basename(entry), gather_leaf)
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
	return cat

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
		cat = Category(title=doc['title'], name=name)
		for leaf in doc['entries']:
			cat.add_leaf(gather_leaf(leaf))
		return cat

def gather_yaml_node(yaml):
	leaf = Leaf(ident=yaml['id'], name=yaml['name'], semantics=yaml.get('semantics'))
	return leaf

def gather_yaml_builtin(yaml):
	leaf = Builtin(ident=yaml['id'], name=yaml['name'], semantics=yaml.get('semantics'), ntype=yaml.get('type'))
	return leaf
