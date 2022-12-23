"""The main application code for astare."""

##############################################################################
# Python imports.
import argparse
from typing             import Any, Final
from pathlib            import Path
from importlib.metadata import version
from functools          import partial

##############################################################################
# Pygments imports.
from pygments.styles import get_all_styles

##############################################################################
# Textual imports.
from textual.app        import App, ComposeResult
from textual.screen     import Screen
from textual.widgets    import Header, Footer, Tree
from textual.containers import Horizontal, Vertical
from textual.binding    import Binding
from textual.timer      import Timer

##############################################################################
# Local imports.
from textual_astview import ASTView, ASTNode, NodeInfo, Source, __version__

##############################################################################
class MainDisplay( Screen ):
    """The main display of the app."""

    DEFAULT_CSS = """
    Vertical {
        width: 1fr;
    }

    ASTView {
        border: solid $primary-background-lighten-2;
    }

    ASTView:focus-within {
        border: double $primary-lighten-2;
    }
    """

    BINDINGS = [
        Binding( "ctrl+q", "app.quit", "Quit" )
    ]
    """list[ Bindings ]: The bindings for the main screen."""

    UPDATE_DELAY: Final = 0.2
    """float: How long to leave it before updating the highlight in the source."""

    def __init__( self, cli_args: argparse.Namespace, *args: Any, **kwargs: Any ) -> None:
        """Initialise the main screen."""
        super().__init__( *args, **kwargs )
        self._args                  = cli_args
        self._refresh: Timer | None = None

    def compose( self ) -> ComposeResult:
        """Compose the main app screen.

        Returns:
            ComposeResult: The result of composing the screen.
        """
        yield Header()
        yield Vertical(
            Horizontal(
                ASTView( self._args.file ),
                Source( self._args.file, theme=self._args.theme )
            ),
            NodeInfo()
        )
        yield Footer()

    def on_mount( self ) -> None:
        """Sort the screen once the DOM is mounted."""
        view = self.query_one( ASTView )
        view.root.expand()
        # Sadly Textual's TreeNode doesn't allow easy access to the
        # children, at the moment, so we're going to do a sneaky dip into
        # the internals here. What I want is to expand up the first couple
        # of levels in the tree, on startup.
        #
        # pylint:disable=protected-access
        if view.root._children:
            view.root._children[ 0 ].expand()
            if view.root._children[ 0 ]._children:
                view.root._children[ 0 ]._children[ 0 ].expand()
        view.focus()

    def highlight_node( self, node: ASTNode ) -> None:
        """Update the display to highlight the given node.

        Args:
            node (ASTNode): The node to highlight.
        """
        self.query_one( NodeInfo ).show( node )
        self.query_one( Source ).highlight( node )

    async def on_astview_node_highlighted( self, event: ASTView.NodeHighlighted ) -> None:
        """React to a node in the tree being highlighted.

        Args:
            event (ASTTree.NodeHighlighted): The event to react to.
        """
        # If there's a refresh pending...
        if self._refresh is not None:
            # ...stop it.
            await self._refresh.stop()
        # Book in a fresh refresh the full delay on from this event.
        self._refresh = self.set_timer(
            self.UPDATE_DELAY, partial( self.highlight_node, event.node )
        )

    async def on_tree_node_selected( self, event: Tree.NodeSelected[ Any ] ):
        """React to a node in the tree being selected.

        Args:
            event (Tree.NodeSelected[ Any ]): The event to react to.
        """
        # If there's a refresh pending...
        if self._refresh is not None:
            # ...stop it and nuke all evidence of it.
            await self._refresh.stop()
            self._refresh = None
        # Selected is a mouse click or someone bouncing on the enter key,
        # there's no point in delaying; so let's make it look a bit more
        # snappy by updating right away.
        self.highlight_node( event.node )


##############################################################################
class Astare( App[ None ] ):
    """Main Textual application class."""

    TITLE = "astare"
    """str: The main title of the app."""

    SUB_TITLE = f"A Python AST Explorer ({__version__})"
    """str: The sub title of the app."""

    def __init__( self, cli_args: argparse.Namespace, *args: Any, **kwargs: Any ) -> None:
        """Initialise the app."""
        super().__init__( *args, **kwargs )
        self._args = cli_args

    def on_mount( self ) -> None:
        """Set up the application on startup."""
        self.push_screen( MainDisplay( self._args ) )

##############################################################################
def py_file( path: str ) -> Path:
    """Check that the file we're being asked to look at seems fine

    Args:
        path (str): The argument.

    Returns:
        Path: The `Path` to the file if it looks okay.
    """

    candidate = Path( path )

    if not candidate.exists():
        raise argparse.ArgumentTypeError( f"{path} does not exist" )

    if not candidate.is_file():
        raise argparse.ArgumentTypeError( f"{path} is not a file" )

    return Path( path )

##############################################################################
def get_args() -> argparse.Namespace:
    """Get the command line arguments.

    Returns:
        argparse.Namespace: The arguments.
    """

    # Create the argument parser object.
    parser = argparse.ArgumentParser(
        prog        = "astare",
        description = "A simple terminal-based AST explorer.",
        epilog      = f"v{__version__}"
    )

    # Add --theme
    parser.add_argument(
        "-t", "--theme",
        choices = list( get_all_styles() ),
        metavar = "THEME",
        default = Source.DEFAULT_THEME,
        help    = "Set the theme for the source display.",
    )

    # Add --themes
    parser.add_argument(
        "--themes",
        action  = "version",
        help    = "List the available theme names.",
        version = ", ".join( sorted( list( get_all_styles() ) ) )
    )

    # Add --version
    parser.add_argument(
        "-v", "--version",
        help    = "Show version information.",
        action  = "version",
        version = f"%(prog)s {__version__} (Textual v{version( 'textual' )})"
    )

    # The reminder is the file to explore.
    parser.add_argument( "file", help="The file to explore", type=py_file )

    # Return the arguments.
    return parser.parse_args()

##############################################################################
def main() -> None:
    """Main entry point for astare."""
    Astare( get_args() ).run()

### astare.py ends here
