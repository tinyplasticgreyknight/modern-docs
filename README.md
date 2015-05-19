# Modern Data documentation project
This is a project to provide more detailed documentation for [Modern Data](https://github.com/IreneKnapp/modern-data).

## Invocation
You will probably first need to modify the `modern-header-file` path in `config.yaml`: this should point to the `modern.h` file from the Modern Data repository.
You should be able to just issue a `make html` or `make latexpdf` command to generate the documentation.
Output should end up in the `build` directory.

### Subcommands (for hacking purposes, or in case make isn't cooperating):
* `python build.py` will generate the ReST documentation in the `rstsource` directory.  This is used as input by Sphinx, but you could read it directly if you want.  Or, perhaps you can use it as input to another tool!
* * `config.yaml` is used to provide some control over how this script works.  The `mask-file` setting is particularly useful for hacking: the named file contains one path per line (e.g. `content/builtins`), and serves to exclude those entries from the build.  This can reduce build times while you're debugging.
* `sphinx-build -b html -d build/doctrees rstsource build/html` will generate HTML documentation from the ReST files.
* `sphinx-build -b html -D latex_paper_size=a4 -d build/doctrees rstsource build/latex` will generate LaTeX documentation from the ReST files.  You can run these through `pdflatex` to get a PDF file, or just run `make all-pdf` in the `build/latex` directory.

## Functionality
We start from the YAML and ReST files in the `content` directory.
The ReST files are mostly just copied across to the `rstsource` directory, and the YAML files are used to generate detailed documentation for heavily-structured things like e.g. builtins.
The YAML files for the C-library functions just list function names and semantics, without specifying a signature: instead, the function signatures are parsed directly from `modern.h` and included in the ReST output.

We also do some validation.  Right now the only validations are:
* ensure that no two builtins have accidentally been assigned the same numeric ID
* ensure that all builtin type signatures resolve down to correctly-named basic types (typo prevention)

## You will need
* Python 3
* `pip install pycparser`
* `pip install pyyaml`
* [Sphinx](http://sphinx-doc.org/latest/install.html) documentation generator
* the `modern.h` header from the [Modern Data repository](https://github.com/IreneKnapp/modern-data) (this file is parsed to extract some type signatures)

### Optionally
* If you want to build PDF output, you will need `pdflatex`.

## Links
* home repository: https://github.com/tinyplasticgreyknight/modern-docs
* Modern Data home repository: https://github.com/IreneKnapp/modern-data
