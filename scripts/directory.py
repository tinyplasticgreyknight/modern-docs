import os, shutil

def expect(dirname):
	if not os.path.isdir(dirname):
		raise IOError("expected directory at %s" % str(dirname))

def remove(dirname):
	shutil.rmtree(dirname)

def remove_if_exists(dirname):
	try:
		remove(dirname)
	except FileNotFoundError:
		pass

def ensure_exists(dirname):
	try:
		os.mkdir(dirname)
	except OSError:
		pass

def copy(source, dest):
	shutil.copytree(source, dest)

def list(root):
	return os.listdir(root)
