"""The main application code for astare."""

##############################################################################
# Python imports.
import argparse
from typing import Any
from pathlib import Path
from importlib.metadata import version

##############################################################################
# Pygments imports.
from pygments.styles import get_all_styles

##############################################################################
# Textual imports.
from textual.app import App

##############################################################################
# Local imports.
from textual_astview import Source, __version__
from .screens import MainDisplay


##############################################################################
class Astare(App[None]):
    """Main Textual application class."""

    TITLE = "astare"
    """The main title of the app."""

    SUB_TITLE = f"A Python AST Explorer ({__version__})"
    """The sub title of the app."""

    def __init__(self, cli_args: argparse.Namespace, *args: Any, **kwargs: Any) -> None:
        """Initialise the app."""
        super().__init__(*args, **kwargs)
        self._args = cli_args

    def on_mount(self) -> None:
        """Set up the application on startup."""
        self.push_screen(MainDisplay(self._args))


##############################################################################
def py_file(path: str) -> Path:
    """Check that the file we're being asked to look at seems fine

    Args:
        path: The argument.

    Returns:
        The `Path` to the file if it looks okay.
    """
    if not (candidate := Path(path)).exists():
        raise argparse.ArgumentTypeError(f"{path} does not exist")
    return candidate


##############################################################################
def get_args() -> argparse.Namespace:
    """Get the command line arguments.

    Returns:
        The arguments.
    """

    # Create the argument parser object.
    parser = argparse.ArgumentParser(
        prog="astare",
        description="A simple terminal-based AST explorer.",
        epilog=f"v{__version__}",
    )

    # Add --dark-theme
    parser.add_argument(
        "-t",
        "--dark-theme",
        choices=list(get_all_styles()),
        metavar="THEME",
        default=Source.DEFAULT_DARK_THEME,
        help="Set the dark mode theme for the source display.",
    )

    # Add --light-theme
    parser.add_argument(
        "-T",
        "--light-theme",
        choices=list(get_all_styles()),
        metavar="THEME",
        default=Source.DEFAULT_LIGHT_THEME,
        help="Set the light mode theme for the source display.",
    )

    # Add --themes
    parser.add_argument(
        "--themes",
        action="version",
        help="List the available theme names.",
        version=", ".join(sorted(list(get_all_styles()))),
    )

    # Add --version
    parser.add_argument(
        "-v",
        "--version",
        help="Show version information.",
        action="version",
        version=f"%(prog)s {__version__} (Textual v{version( 'textual' )})",
    )

    # The remainder is the file to explore.
    parser.add_argument(
        "file", help="The file to explore", type=py_file, default=".", nargs="?"
    )

    # Return the arguments.
    return parser.parse_args()


##############################################################################
def main() -> None:
    """Main entry point for astare."""
    Astare(get_args()).run()


### astare.py ends here
