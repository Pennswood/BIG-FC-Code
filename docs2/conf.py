# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'Oasis'
copyright = '2020, Penn State SSPL'
author = 'Penn State SSPL'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc','sphinx.ext.napoleon','sphinx.ext.intersphinx']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

#DEPRICATED
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

html_logo = 'sspl.png'

# -- Napolean Extension -------------------------------------------------------------------

# This will enable the usage of google and numpy docstrings

napoleon_google_docstring = True			# Enable for Google docstrings
napoleon_numpy_docstring = True				# Enable for Numpy docstrings
napoleon_include_init_with_doc = False		# Enable this for the use of docstrings in init
napoleon_include_private_with_doc = False 	# Enable to add private methods' docstrings
napoleon_include_special_with_doc = True 	# Used for docstrings in special python methods
napoleon_use_admonition_for_examples = False	# Used for example docstrings
napoleon_use_admonition_for_notes = False		# Used for note docstrings
napoleon_use_admonition_for_references = False	# Used for reference docstrings
napoleon_use_ivar = False					# Used for instance variables
napoleon_use_param = True					# Used for Parameter type docstrings
napoleon_use_rtype = True					# Used for return type docstrings

# -- Intersphinx API Links ----------------------------------------------------

# Enabling intersphinx allows for the addition of links to used resources in
# Oasis packages

intersphinx_mapping = {'python': ('https://docs.python.org/', None)}