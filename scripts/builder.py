import os.path
import subprocess

BUILDERS = {}

def build(target, config):
	builder = BUILDERS[target]
	builder(config)

def mark(f):
	BUILDERS[f.__name__] = f
	return f

def create_simple(target):
	def _builder(config):
		build("regen", config)
		sphinx(target, config)
	_builder.__name__ = target
	BUILDERS[target] = _builder

def submake(build_subdir, target, config):
	make = config['make-command']
	directory = "%s/%s" % (config['build-dir'], build_subdir)
	subprocess.call([make, "-C", directory, target])

def sphinx(target, config, *args):
	print("==== building sphinx target [%s] ====" % target)
	doctrees = os.path.normpath("%s/doctrees" % config['build-dir'])
	output_dir = os.path.normpath("%s/%s" % (config['build-dir'], target))
	sphinx_build = config['sphinx-build-command']
	cmd = [sphinx_build, "-b", target] + list(args) + ["-d", doctrees, config['source-dir'], output_dir]
	subprocess.call(cmd)
