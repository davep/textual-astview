"""Setup file for the textual-astview application."""

##############################################################################
# Python imports.
from pathlib    import Path
from setuptools import setup, find_packages

##############################################################################
# Import the library itself to pull details out of it.
import textual_astview

##############################################################################
# Work out the location of the README file.
def readme():
    """Return the full path to the README file.

    :returns: The path to the README file.
    :rtype: ~pathlib.Path
    """
    return Path( __file__ ).parent.resolve() / "README.md"

##############################################################################
# Load the long description for the package.
def long_desc():
    """Load the long description of the package from the README.

    :returns: The long description.
    :rtype: str
    """
    with readme().open( "r", encoding="utf-8" ) as rtfm:
        return rtfm.read()

##############################################################################
# Perform the setup.
setup(

    name                          = "textual-astview",
    version                       = textual_astview.__version__,
    description                   = str( textual_astview.__doc__ ),
    long_description              = long_desc(),
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/davep/textual-astview",
    author                        = textual_astview.__author__,
    author_email                  = textual_astview.__email__,
    maintainer                    = textual_astview.__maintainer__,
    maintainer_email              = textual_astview.__email__,
    packages                      = find_packages(),
    package_data                  = { "textual_astview": [ "py.typed" ] },
    include_package_data          = True,
    install_requires              = [ "textual==0.8.0" ],
    python_requires               = ">=3.9",
    keywords                      = "terminal library widget tool ast abstract syntax tree viewer explorer",
    entry_points                  = {
        "console_scripts": "astare=textual_astview.app.astare:main"
    },
    license                       = (
        "License :: OSI Approved :: MIT License"
    ),
    classifiers                   = [
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Terminals",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries",
        "Typing :: Typed"
    ]

)

### setup.py ends here
