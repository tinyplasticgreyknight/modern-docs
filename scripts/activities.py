import os, sys, shutil
import io
import gather
import directory
import diffs
import verify

def verify_docs(root):
	for child in root.children:
		verify.consistency(child)

def create_rest_tree(root, source_dir, sphinx_conf_filename):
	root.create_tree(source_dir)
	directory.ensure_exists(os.path.join(source_dir, "_static"))
	shutil.copy(sphinx_conf_filename, os.path.join(source_dir, "conf.py"))

def gather_docs(mask, content_dir):
	root = gather.directory(None, ".", content_dir, mask=mask)
	root.name = None
	root.is_root = True
	#root.toc_depth = 2
	return root

def load_masks(mask_filename):
	try:
		with io.open(mask_filename, 'r') as f:
			return [os.path.normpath(line.strip()) for line in f]
	except IOError:
		# if file is not present, treat it as empty
		return []

def compute_diff(expected, actual):
	directory.expect(expected)
	directory.expect(actual)
	return diffs.tree(expected, actual)

def show_diff(diff, accum=""):
	for name, item in diff.items():
		thispath = os.path.join(accum, name)
		builder.report("difference in [%s]", thispath)
		if type(item) == list:
			for line in item:
				sys.stdout.write(line)
		else:
			show_diff(item, thispath)
