import os.path
import subprocess

BUILDERS = {}

def build(target, config):
	builder = BUILDERS[target]
	builder(config)

def report(msg, *values):
	formatted_msg = msg % values
	print("==== %s ====" % formatted_msg)

def progress(msg, *values):
	formatted_msg = msg % values
	print("---- %s ----" % formatted_msg)

def note(msg, *values):
	print(("note: " + msg) % values)

def mark(f):
	target = f.__name__
	def _decorated(config):
		report("building target [%s]", target)
		f(config)
	_decorated.__name__ = target
	BUILDERS[target] = _decorated
	return _decorated

def create_simple(target):
	def _builder(config):
		report("building target [%s]", target)
		note("regenerating ReST files first")
		build("regen", config)
		sphinx(target, config)
	_builder.__name__ = target
	BUILDERS[target] = _builder

def submake(build_subdir, target, config):
	report("calling make [%s] for [%s]", target, build_subdir)
	make = config['make-command']
	directory = "%s/%s" % (config['build-dir'], build_subdir)
	subprocess.call([make, "-C", directory, target])

def sphinx(target, config, *args):
	report("building sphinx target [%s]", target)
	doctrees = os.path.normpath("%s/doctrees" % config['build-dir'])
	output_dir = os.path.normpath("%s/%s" % (config['build-dir'], target))
	sphinx_build = config['sphinx-build-command']
	cmd = [sphinx_build, "-b", target] + list(args) + ["-d", doctrees, config['rest-dir'], output_dir]
	subprocess.call(cmd)
