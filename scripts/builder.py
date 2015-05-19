BUILDERS = {}

def build(target, config):
	builder = BUILDERS[target]
	builder(config)

def mark(f):
	BUILDERS[f.__name__] = f
	return f
