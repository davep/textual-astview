"""The main application code for astare."""

##############################################################################
# Python imports.
import argparse
from typing  import Any
from pathlib import Path

##############################################################################
# Textual imports.
from textual.app        import App, ComposeResult
from textual.screen     import Screen
from textual.widgets    import Header, Footer
from textual.containers import Horizontal, Vertical

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

    def __init__( self, explore: Path, *args: Any, **kwargs: Any ) -> None:
        """Initialise the main screen."""
        super().__init__( *args, **kwargs )
        self._explore = explore

    def compose( self ) -> ComposeResult:
        """Compose the main app screen.

        Returns:
            ComposeResult: The result of composing the screen.
        """
        yield Header()
        yield Vertical(
            Horizontal(
                ASTView( self._explore ),
                Source( self._explore )
            ),
            NodeInfo()
        )
        yield Footer()

    def on_mount( self ) -> None:
        """Sort the screen once the DOM is mounted."""
        view = self.query_one( ASTView )
        view.root.expand()
        view.root._children[ 0 ].expand()
        view.root._children[ 0 ]._children[ 0 ].expand()
        view.focus()

    def highlight_node( self, node: ASTNode ) -> None:
        """Update the display to highlight the given node.

        Args:
            node (ASTNode): The node to highlight.
        """
        self.query_one( NodeInfo ).show( node )
        self.query_one( Source ).highlight( node )

    def on_astview_node_highlighted( self, event: ASTView.NodeHighlighted ):
        """React to a node in the tree being highlighted.

        Args:
            event (Tree.NodeSelected[ Any ]): The event to react to.
        """
        self.highlight_node( event.node )

##############################################################################
class Astare( App[ None ] ):
    """Main Textual application class."""

    TITLE = "astare"
    """str: The main title of the app."""

    SUB_TITLE = f"A Python AST Explorer ({__version__})"
    """str: The sub title of the app."""

    def __init__( self, explore: Path, *args: Any, **kwargs: Any ) -> None:
        """Initialise the app."""
        super().__init__( *args, **kwargs )
        self._explore = explore

    def on_mount( self ) -> None:
        """Set up the application on startup."""
        self.push_screen( MainDisplay( self._explore ) )

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
        epilog      = __version__
    )

    # Add --version
    parser.add_argument(
        "-v", "--version",
        help    = "Show version information.",
        action  = "version",
        version = f"%(prog)s {__version__}"
    )

    # The reminder is the file to explore.
    parser.add_argument( "file", help="The file to explore" )

    # Return the arguments.
    return parser.parse_args()

##############################################################################
def main() -> None:
    """Main entry point for astare."""

    # Parse the arguments.
    args = get_args()

    # Explore the file.
    Astare( Path( args.file ) ).run()

### astare.py ends here
