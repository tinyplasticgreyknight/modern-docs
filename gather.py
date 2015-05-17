import os
import io
import yaml
from categorisation import *

def gather_directory(title, path_prefix, dirname, gather_leaf):
	cat = Category(title=title, name=dirname)
	scan_path = os.path.join(path_prefix, dirname)
	for entry in os.listdir(scan_path):
		full_entry = os.path.join(scan_path, entry)
		if os.path.isdir(full_entry):
			subdir = gather_directory(entry, scan_path, os.path.basename(entry), gather_leaf)
			cat.add_child(subdir)
			continue
		suffix = os.path.splitext(entry)[1]
		if os.path.isfile(full_entry) and suffix == '.yaml':
			cat.add_child(gather_yaml_category(full_entry, gather_leaf))
	return cat

def gather_yaml_category(yamlfile, gather_leaf):
	with io.open(yamlfile, 'r') as f:
		doc = yaml.load(f)
		try:
			name = doc['name']
		except KeyError:
			name = os.path.splitext(os.path.basename(yamlfile))[0]
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
