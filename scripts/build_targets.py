import os, sys, shutil
import subprocess
from gather import *
from funcs import *
from verify import *
from clibrary import parse_library_header, apply_types_for_c
import builder

#=============================================================================

@builder.mark
def regen(config):
	masks = load_masks(config['mask-file'])
	builder.progress("gathering data")
	root = gather_docs(masks, config['content-dir'])
	builder.progress("examining header")
	ast = parse_library_header(config['modern-header-file'])
	builder.progress("applying extracted C types")
	apply_types_for_c(root, ast)
	builder.progress("verifying consistency")
	verify_docs(root)
	builder.progress("creating ReST tree")
	create_rest_tree(root, config['rest-dir'], config['sphinx-conf'])
	return True

builder.create_simple("html")
builder.create_simple("texinfo")
builder.create_simple("dirhtml")
builder.create_simple("singlehtml")
builder.create_simple("pickle")
builder.create_simple("json")
builder.create_simple("epub")
builder.create_simple("text")
builder.create_simple("man")
builder.create_simple("gettext")
builder.create_simple("changes")
builder.create_simple("linkcheck")
builder.create_simple("doctest")
builder.create_simple("xml")
builder.create_simple("pseudoxml")

@builder.mark
def latex(config):
	builder.dependency("regen", config)

	latex_paper_size = "latex_paper_size=%s" % config['latex-paper-size']
	builder.sphinx("latex", config, "-D", latex_paper_size)
	return True

@builder.mark
def pdf(config):
	builder.dependency("latex", config)
	builder.submake("latex", "all-pdf", config)
	return True

@builder.mark
def pdfja(config):
	builder.dependency("latex", config)
	builder.submake("latex", "all-pdf-ja", config)
	return True

@builder.mark
def info(config):
	builder.dependency("texinfo", config)
	builder.submake("texinfo", "info", config)
	return True

@builder.mark
def clean(config):
	clean_dir(config['rest-dir'])
	clean_dir(config['build-dir'])
	return True

@builder.mark
def showmasks(config):
	masks = load_masks(config['mask-file'])
	if len(masks) == 0:
		print("No masks are loaded")
		return
	print("The following paths are masked:")
	for mask in masks:
		print("* %s" % mask)
	return True

@builder.mark
def bless(config):
	expect_directory(config['rest-dir'])
	remove_dir_if_exists(config['blessed-copy'])
	builder.progress("blessing ReST files")
	shutil.copytree(config['rest-dir'], config['blessed-copy'])
	return True

@builder.mark
def checkblessed(config):
	actual = config['rest-dir']
	expected = config['blessed-copy']
	expect_directory(expected)
	expect_directory(actual)
	diff = tree_diff(expected, actual)
	if len(diff) == 0:
		builder.progress("successful match with blessed copy")
		return True
	else:
		builder.progress("mismatch")
		show_diff(diff)
		return False

#=============================================================================

def verify_docs(root):
	for child in root.children:
		verify_consistency(child)

def create_rest_tree(root, source_dir, sphinx_conf_filename):
	root.create_tree(source_dir)
	ensure_dir_exists(os.path.join(source_dir, "_static"))
	shutil.copy(sphinx_conf_filename, os.path.join(source_dir, "conf.py"))

def gather_docs(mask, content_dir):
	root = gather_directory(None, ".", content_dir, mask=mask)
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

def clean_dir(dir_name):
	if os.path.isdir(dir_name):
		shutil.rmtree(dir_name)

def show_diff(diff, accum=""):
	for name, item in diff.items():
		thispath = os.path.join(accum, name)
		builder.report("difference in [%s]", thispath)
		if type(item) == list:
			for line in item:
				sys.stdout.write(line)
		else:
			show_diff(item, thispath)
