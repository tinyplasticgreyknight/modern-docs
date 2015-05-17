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
	root = gather_directory(None, ".", "content")
	root.name = None
	root.is_root = True
	#root.toc_depth = 2
	return root

main(*sys.argv[1:])
