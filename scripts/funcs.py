import os, sys, shutil
import io
import difflib

def expect_directory(dirname):
	if not os.path.isdir(dirname):
		raise IOError("expected directory at %s" % str(dirname))

def remove_dir_if_exists(dirname):
	try:
		shutil.rmtree(dirname)
	except FileNotFoundError:
		pass

def ensure_dir_exists(dirname):
	try:
		os.mkdir(dirname)
	except OSError:
		pass

def tree_diff(expected, actual):
	expected_outline = tree_listing(expected)
	actual_outline = tree_listing(actual)
	diff = {}
	for filename in expected_outline:
		if not filename in actual_outline:
			expected_name = os.path.join(expected, filename)
			diff[filename] = fso_diff("exists", "absent")
	for filename in actual_outline:
		expected_name = os.path.join(expected, filename)
		actual_name = os.path.join(actual, filename)
		if not filename in expected_outline:
			diff[filename] = fso_diff("absent", "exists")
			continue
		if os.path.isdir(expected_name):
			if not os.path.isdir(actual_name):
				diff[filename] = fso_diff("directory", "non-directory")
				continue
			subdiff = tree_diff(expected_name, actual_name)
		else:
			if os.path.isdir(actual_name):
				diff[filename] = fso_diff("non-directory", "directory")
				continue
			subdiff = file_diff(expected_name, actual_name)
		if len(subdiff) > 0:
			diff[filename] = subdiff
	return diff

def fso_diff(expected, actual):
	return [
		"--- (blessed %s)\n" % expected,
		"+++ (actual %s)\n" % actual,
	]

def file_diff(expected, actual):
	expected_lines = io.open(expected, 'r').readlines()
	actual_lines = io.open(actual, 'r').readlines()
	delta_lines = difflib.unified_diff(expected_lines, actual_lines, "blessed", "actual")
	return list(delta_lines)

def tree_listing(root):
	return os.listdir(root)

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
