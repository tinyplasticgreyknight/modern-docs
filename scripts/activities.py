def verify_docs(root):
	for child in root.children:
		verify_consistency(child)

def create_rest_tree(root, source_dir, sphinx_conf_filename):
	root.create_tree(source_dir)
	ensure_dir_exists(os.path.join(source_dir, "_static"))
	shutil.copy(sphinx_conf_filename, os.path.join(source_dir, "conf.py"))

def gather_docs(mask, content_dir, header_filename):
	root = gather_directory(None, ".", content_dir, mask=mask)
	root.name = None
	root.is_root = True
	#root.toc_depth = 2
	ast = parse_library_header(header_filename)
	apply_types_for_c(root, ast)
	return root

def load_masks(mask_filename):
	masks = []
	try:
		with io.open(mask_filename, 'r') as f:
			for line in f:
				masks.append(os.path.normpath(line.strip()))
	except IOError:
		pass
	return masks
