"""Setup file for the textual-astview application."""

##############################################################################
# Python imports.
import re
from collections import defaultdict
from pathlib import Path

from setuptools import find_packages, setup


PACKAGE = "textual_astview"


def load_init(file=Path(f"{PACKAGE}/__init__.py")):
    source = file.read_text(encoding="utf-8")
    _var_init = defaultdict(lambda: "")

    match = re.search(r'["]{3}(.*)["]{3}', source)
    if match:
        _var_init["__doc__"] = f"{match.groups(0)[0]}"

    match = re.findall(r'([_]{2}[a-z]+[_]{2})\s+=\s+["\']{1}(.+)["\']{1}', source)
    if match:
        _var_init.update(dict(match))
    return _var_init


vars_init = load_init()


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

    name                          = f"{PACKAGE}".replace("_","-"),
    version                       = vars_init["__version__"],
    description                   = vars_init["__doc__"],
    long_description              = long_desc(),
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/davep/textual-astview",
    author                        = vars_init["__author__"],
    author_email                  = vars_init["__email__"],
    maintainer                    = vars_init["__maintainer__"],
    maintainer_email              = vars_init["__email__"],
    packages                      = find_packages(),
    package_data                  = { f"{PACKAGE}": [ "py.typed" ] },
    include_package_data          = True,
    install_requires              = [ "textual==0.7.0" ],
    python_requires               = ">=3.9",
    keywords                      = "terminal library widget tool ast abstract syntax tree viewer explorer",
    entry_points                  = {
        f"console_scripts": f"astare={PACKAGE}.app.astare:main"
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
