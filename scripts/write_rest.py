import os, sys, shutil
import io

REST_HEADER_LEVELS = ["=", "-", "~"]
def write_rest_header(stream, text, level=0):
	kind = REST_HEADER_LEVELS[level]
	stream.write("%s\n" % text)
	stream.write("%s\n" % (kind * len(text)))
	stream.write("\n")

def write_index(stream, category):
	write_index_header(stream, category)
	write_index_intro(stream, category)
	if category.print_toc_as_struct:
		write_index_toc_struct(stream, category)
	else:
		write_index_toc(stream, category)
	write_index_contents(stream, category)
	write_index_footer(stream, category)

def write_index_header(stream, category):
	if not category.has_own_header:
		write_rest_header(stream, category.title, 0)

def write_index_intro(stream, category):
	if category.intro_text is not None:
		stream.write(category.intro_text)
		stream.write("\n")

def write_index_toc(stream, category):
	if category.toc_depth > 0:
		stream.write(".. toctree::\n")
		stream.write("   :maxdepth: %d\n" % category.toc_depth)
		stream.write("\n")

	for child in category.ordered_children():
		stream.write("   %s\n" % child.toc_entry())

	for leaf in category.leaves:
		stream.write("   %s\n" % leaf.name)

def write_index_toc_struct(stream, category):
	stream.write("| ``struct %s {``\n" % category.name)
	for leaf in category.leaves:
		link = struct_field_link(category.name, leaf.name)
		stream.write("|\t``%s`` %s ``;``\n" % (str(leaf.type), link))
	stream.write("| ``}``\n")

def struct_field_link(struct_name, field_name):
	return "`%s`_" % anchor_name(struct_name, field_name)

def write_struct_field_anchor(stream, struct_name, field_name):
	pass

def anchor_name(struct_name, field_name):
	return field_name

def write_index_contents(stream, category):
	if category.contents is not None:
		stream.write(category.contents)
		stream.write("\n")

def write_index_footer(stream, category):
	if category.is_root:
		write_indices_and_tables(stream)

def write_indices_and_tables(stream):
	stream.write("\n")
	write_rest_header(stream, "Indices and tables", 0)
	stream.write("* :ref:`genindex`\n")
	stream.write("* :ref:`search`\n")
