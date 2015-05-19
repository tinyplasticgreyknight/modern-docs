# Modern Data documentation project
This is a project to provide more detailed documentation for [Modern Data](https://github.com/IreneKnapp/modern-data).

## Invocation
You will probably first need to modify the `MAIN_REPO_ROOT` path in `make-rest.py`: this should point to the `modern.h` file from the Modern Data repository.
You should be able to just issue a `make html` or `make latexpdf` command to generate the documentation.
Output should end up in the `build` directory.

Subcommands (for hacking purposes, or in case make isn't cooperating):
* `python make-rest.py rstsource` will generate the ReST documentation in the `rstsource` directory.  This is used as input by Sphinx, but you could read it directly if you want.  Or, perhaps you can use it as input to another tool!
* `sphinx-build -b html -d build/doctrees rstsource build/html` will generate HTML documentation from the ReST files.
* `sphinx-build -b html -D latex_paper_size=a4 -d build/doctrees rstsource build/latex` will generate LaTeX documentation from the ReST files.  You can run these through `pdflatex` to get a PDF file.

## Functionality
We start from the YAML and ReST files in the `content` directory.
The ReST files are mostly just copied across to the `rstsource` directory, and the YAML files are used to generate detailed documentation for heavily-structured things like e.g. builtins.
The YAML files for the C-library functions just list function names and semantics, without specifying a signature: instead, the function signatures are parsed directly from `modern.h` and included in the ReST output.

We also do some validation.  Right now the only validations are:
* ensure that no two builtins have accidentally been assigned the same numeric ID
* ensure that all builtin type signatures resolve down to correctly-named basic types (typo prevention)

## You will need
* Python 3
* pycparser (available via `pip install pycparser`)
* [Sphinx](http://sphinx-doc.org/latest/install.html) documentation generator

## Links
* home repository: https://github.com/tinyplasticgreyknight/modern-docs
* Modern Data home repository: https://github.com/IreneKnapp/modern-data
