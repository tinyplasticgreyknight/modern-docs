#!/usr/bin/env python3

import sys
import io
import yaml
sys.path.append("scripts")
import builder
import build_targets

CONFIG_FILE = "config.yaml"

def load_config():
	with io.open(CONFIG_FILE, 'r') as f:
		return yaml.load(f.read())

def main(target="regen"):
	try:
		builder.build(target, load_config())
		builder.report("everything is okay")
	except Exception as e:
		import traceback
		builder.report("something went wrong [%s]", e.__class__.__name__)
		for earg in e.args:
			print(earg)
		builder.report("stack trace")
		trace = sys.exc_info()[2]
		traceback.print_tb(trace, None, sys.stdout)

main(*sys.argv[1:])
