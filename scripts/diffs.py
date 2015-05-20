import os
import io
import difflib
import directory

def tree(expected, actual):
	expected_outline = directory.list(expected)
	actual_outline = directory.list(actual)
	diff = {}
	for filename in expected_outline:
		if not filename in actual_outline:
			expected_name = os.path.join(expected, filename)
			diff[filename] = fso("exists", "absent")
	for filename in actual_outline:
		expected_name = os.path.join(expected, filename)
		actual_name = os.path.join(actual, filename)
		if not filename in expected_outline:
			diff[filename] = fso("absent", "exists")
			continue
		if os.path.isdir(expected_name):
			if not os.path.isdir(actual_name):
				diff[filename] = fso("directory", "non-directory")
				continue
			subdiff = tree(expected_name, actual_name)
		else:
			if os.path.isdir(actual_name):
				diff[filename] = fso("non-directory", "directory")
				continue
			subdiff = textfile(expected_name, actual_name)
		if len(subdiff) > 0:
			diff[filename] = subdiff
	return diff

def fso(expected, actual):
	return [
		"--- (blessed %s)\n" % expected,
		"+++ (actual %s)\n" % actual,
	]

def textfile(expected, actual):
	expected_lines = io.open(expected, 'r').readlines()
	actual_lines = io.open(actual, 'r').readlines()
	delta_lines = difflib.unified_diff(expected_lines, actual_lines, "blessed", "actual")
	return list(delta_lines)
