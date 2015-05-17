import os

def ensure_dir_exists(dirname):
	try:
		os.mkdir(dirname)
	except OSError:
		pass

def write_rest_header(stream, text, kind="="):
	stream.write("%s\n" % text)
	stream.write("%s\n" % (kind * len(text)))
	stream.write("\n")

def write_index(stream, category):
	write_rest_header(stream, category.title, "=")

	if category.intro_text is not None:
		stream.write(category.intro_text)
		stream.write("\n")

	stream.write(".. toctree::\n")
	stream.write("   :maxdepth: %d\n" % category.toc_depth)
	stream.write("\n")

	for child in category.ordered_children():
		stream.write("   %s/index\n" % child.name)

	for leaf in category.leaves:
		stream.write("   %s\n" % leaf.name)

	if category.contents is not None:
		stream.write(category.contents)
		strem.write("\n")

	if category.is_root:
		write_indices_and_tables(stream)

def write_indices_and_tables(stream):
	stream.write("\n")
	write_rest_header(stream, "Indices and tables", "=")
	stream.write("* :ref:`genindex`\n")
	stream.write("* :ref:`search`\n")
