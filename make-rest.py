#!/usr/bin/env python

import os, sys, shutil
from categorisation import *
from gather import *
from funcs import *
from verify import *
from clibrary import parse_library_header, apply_types_for_c_functions

MAIN_REPO_ROOT = "../modern-data"
CONTENT_DIR = "content"
SPHINX_CONF = "sphinx-conf.py"
MASK_FILE = "mask.user"

def main(source_dir):
	root = gather_docs(mask())
	for child in root.children:
		verify_consistency(child)
	root.create_tree(source_dir)
	ensure_dir_exists(os.path.join(source_dir, "_static"))
	shutil.copy(SPHINX_CONF, os.path.join(source_dir, "conf.py"))

def gather_docs(mask):
	root = gather_directory(None, ".", CONTENT_DIR, mask=mask)
	root.name = None
	root.is_root = True
	#root.toc_depth = 2
	ast = parse_library_header(os.path.join(MAIN_REPO_ROOT, "C", "library", "modern.h"))
	apply_types_for_c_functions(root, ast)
	return root

def mask():
	masks = []
	try:
		with io.open(MASK_FILE, 'r') as f:
			for line in f:
				masks.append(os.path.normpath(line.strip()))
	except IOException:
		pass
	return masks

main(*sys.argv[1:])
