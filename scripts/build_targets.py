import subprocess
import builder
import activities
import clibrary
import directory

@builder.mark
def help(config):
	print("Invoke as \"./build.py TARGET\", where TARGET is one of the following:")
	targets = sorted(builder.available_targets())
	for target in targets:
		print("* %s" % target)
	return True

@builder.mark
def regen(config):
	masks = activities.load_masks(config['mask-file'])
	builder.progress("gathering data")
	root = activities.gather_docs(masks, config['content-dir'])
	builder.progress("examining header")
	ast = clibrary.parse_library_header(config['modern-header-file'])
	builder.progress("applying extracted C types")
	clibrary.apply_types_for_c(root, ast)
	builder.progress("verifying consistency")
	activities.verify_docs(root)
	builder.progress("creating ReST tree")
	activities.create_rest_tree(root, config['rest-dir'], config['sphinx-conf'])
	return True

@builder.mark
def verify(config):
	masks = activities.load_masks(config['mask-file'])
	builder.progress("gathering data")
	root = activities.gather_docs(masks, config['content-dir'])
	builder.progress("examining header")
	ast = clibrary.parse_library_header(config['modern-header-file'])
	builder.progress("applying extracted C types")
	clibrary.apply_types_for_c(root, ast)
	builder.progress("verifying consistency")
	activities.verify_docs(root)
	return True

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
	directory.remove_if_exists(config['rest-dir'])
	directory.remove_if_exists(config['build-dir'])
	return True

@builder.mark
def showmasks(config):
	masks = activities.load_masks(config['mask-file'])
	if len(masks) == 0:
		print("No masks are loaded")
		return
	print("The following paths are masked:")
	for mask in masks:
		print("* %s" % mask)
	return True

@builder.mark
def bless(config):
	directory.expect(config['rest-dir'])
	directory.remove_if_exists(config['blessed-copy'])
	builder.progress("blessing ReST files")
	directory.copy(config['rest-dir'], config['blessed-copy'])
	return True

@builder.mark
def checkblessed(config):
	diff = activities.compute_diff(config['blessed-copy'], config['rest-dir'])
	if len(diff) == 0:
		builder.progress("successful match with blessed copy")
		return True
	else:
		builder.progress("mismatch")
		activities.show_diff(diff)
		return False

builder.create_simple("changes")
builder.create_simple("dirhtml")
builder.create_simple("doctest")
builder.create_simple("epub")
builder.create_simple("gettext")
builder.create_simple("html")
builder.create_simple("json")
builder.create_simple("linkcheck")
builder.create_simple("man")
builder.create_simple("pickle")
builder.create_simple("pseudoxml")
builder.create_simple("singlehtml")
builder.create_simple("texinfo")
builder.create_simple("text")
builder.create_simple("xml")
