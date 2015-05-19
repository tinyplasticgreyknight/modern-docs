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
	builder.build(target, load_config())

main(*sys.argv[1:])
