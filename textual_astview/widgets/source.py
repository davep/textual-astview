"""Provides a widget for displaying the source related to the AST view."""

##############################################################################
# Python imports.
from pathlib import Path
from typing  import Any, ClassVar

##############################################################################
# Rich imports.
from rich.syntax import Syntax

##############################################################################
# Textual imports.
from textual          import events
from textual.app      import ComposeResult
from textual.widgets  import Static
from textual.geometry import Region

##############################################################################
# Local imports.
from .astview     import ASTNode
from .source_info import SourceInfo

##############################################################################
class Source( SourceInfo, can_focus=True ):
    """Displays the source code for the file."""

    COMPONENT_CLASSES: ClassVar[ set[ str ] ] = {
        "source--ast-node-highlight"
    }
    """set[ str ]: Classes that can be used to style the source view."""

    DEFAULT_CSS = """
    Source {
        height: 1fr;
        border: solid $primary-background-lighten-2;
        background: $panel;
    }

    Source:focus {
        border: double $primary-lighten-2;
    }

    Source > .source--ast-node-highlight {
        color: white;
        background: red;
        text-style: italic;
    }
    """

    def __init__( self, source: Path, *args: Any, **kwargs: Any ) -> None:
        """Initialise the source viewing widget."""
        super().__init__( *args, **kwargs )
        self._source = Syntax.from_path( str( source ), line_numbers=True, lexer="python" )

    def compose( self ) -> ComposeResult:
        """Compose the source display.

        Returns:
            ComposeResult: The result of composing the source display.
        """
        yield Static( self._source )

    def on_click( self, _: events.Click ) -> None:
        """React to a mouse click."""
        self.focus()

    def highlight( self, node: ASTNode ) -> None:
        """Highlight the given AST data in the source.

        Args:
            node (ASTNode): The AST node to highlight.
        """

        # Sneaky nuking of any old styles. Rich's `Syntax` doesnt' allow for
        # removing any stylized ranges so, other than nuking the while
        # Syntax and generating it again every time (slow!), the only option
        # we've got is to kill the list via an internal.
        #
        # pylint:disable=protected-access
        self._source._stylized_ranges = []

        # If the node we're looking at has AST location data...
        if ( loc := self.file_location_of( node ) ) is not None:
            self._source.stylize_range(
                self.get_component_rich_style( "source--ast-node-highlight", partial=True ), loc[ :2 ], loc[ 2: ]
            )
            line, _, end_line, _ = loc
            self.scroll_to_region( Region( y=line - 1, height=( end_line - line ) + 1 ) )

        # Update the display.
        self.query_one( Static ).refresh()

### source.py ends here
