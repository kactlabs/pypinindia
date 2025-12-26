# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath("../../"))


project = 'pypinindia'
copyright = '2025, Kact Labs'
author = 'Kact Labs'
release = '0.1.14'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]

autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "imported-members": False,
}

# Treat __all__ as the public API if present
autodoc_preserve_defaults = True

# Prevent Sphinx from creating multiple targets for the same symbol
autodoc_typehints = "description"

# Do not generate cross-reference targets for type hints
autodoc_typehints_format = "short"

# --- Suppress known, non-actionable warnings ---
suppress_warnings = [
    "ref.python",
    "docutils",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
