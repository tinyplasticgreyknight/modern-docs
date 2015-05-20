import os.path
import subprocess

BUILDERS = {}

def build(target, config):
	report("building target [%s]", target)
	builder = BUILDERS[target]
	return builder(config)

def available_targets():
	return BUILDERS.keys()

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
	BUILDERS[target] = f
	return f

def create_simple(target):
	def _builder(config):
		dependency("regen", config)
		sphinx(target, config)
		return True
	_builder.__name__ = target
	BUILDERS[target] = _builder

def dependency(target, config):
	report("building dependency [%s]", target)
	builder = BUILDERS[target]
	builder(config)

def submake(build_subdir, target, config):
	report("calling make [%s] for [%s]", target, build_subdir)
	make = config['make-command']
	directory = "%s/%s" % (config['build-dir'], build_subdir)
	subprocess.call([make, "-C", directory, target])

def sphinx(target, config, *args):
	report("calling sphinx builder [%s]", target)
	doctrees = os.path.normpath("%s/doctrees" % config['build-dir'])
	output_dir = os.path.normpath("%s/%s" % (config['build-dir'], target))
	sphinx_build = config['sphinx-build-command']
	cmd = [sphinx_build, "-b", target] + list(args) + ["-d", doctrees, config['rest-dir'], output_dir]
	subprocess.call(cmd)
