#!/usr/bin/env python

import os, sys, shutil
from categorisation import *
from gather import *
from funcs import *
from verify import *

def main(source_dir):
	root = gather_docs()
	for child in root.children:
		verify_consistency(child)
	root.create_tree(source_dir)
	ensure_dir_exists(os.path.join(source_dir, "_static"))
	shutil.copy("sphinx-conf.py", os.path.join(source_dir, "conf.py"))

def gather_docs():
	root = Category(title="Modern, the data/schema format", toc_depth=2)
	root.add_child(gather_directory("Builtin Identifiers", ".", "builtins", gather_yaml_builtin))
	root.add_child(gather_directory("Nodes", ".", "nodes", gather_yaml_node))
	return root

main(*sys.argv[1:])