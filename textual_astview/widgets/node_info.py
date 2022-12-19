"""Provides a widget for displaying information about a node from the AST tree."""

##############################################################################
# Textual imports.
from textual.app     import ComposeResult
from textual.widgets import Static

##############################################################################
# Local imports.
from .astview     import ASTNode
from .source_info import SourceInfo

##############################################################################
class NodeInfo( SourceInfo ):
    """Displays some information about the node."""

    DEFAULT_CSS = """
    NodeInfo {
        background: $panel;
        padding-left: 1;
        height: 1;
        border: none;
    }

    NodeInfo Static#--node-path {
        width: 1fr;
    }

    NodeInfo Static#--node-location {
        dock: right;
        width: 20;
    }
    """

    def compose( self ) -> ComposeResult:
        """Compose the main app screen.

        Returns:
            ComposeResult: The result of composing the screen.
        """
        yield Static( id="--node-path")
        yield Static( id="--node-location" )

    def show( self, node: ASTNode ) -> None:
        """Show some details for the given node.

        Args:
            node (ASTNode): The node to show the data for.
        """
        if ( loc := self.file_location_of( node ) ) is not None:
            self.query_one( "#--node-location", Static ).update(
                f"{loc[ 0 ]:04d}:{loc[ 1 ]:03d} -> {loc[ 2 ]:04d}:{loc[ 3 ]:03d}"
            )
        else:
            self.query_one( "#--node-location", Static ).update( "" )
        self.query_one( "#--node-path", Static ).update(
            " > ".join( reversed( list( self.path_from( node ) ) ) )
        )

### node_info.py ends here
