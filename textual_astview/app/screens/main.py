"""Main screen for astare."""

##############################################################################
# Python imports.
from typing    import Final, Any, cast, Optional
from argparse  import Namespace
from functools import partial
from pathlib   import Path

##############################################################################
# Textual imports.
from textual.app        import ComposeResult
from textual.binding    import Binding
from textual.screen     import Screen
from textual.reactive   import reactive
from textual.timer      import Timer
from textual.widgets    import Header, Footer, Tree, DirectoryTree
from textual.containers import Horizontal, Vertical
from textual.css.query  import NoMatches

##############################################################################
# Local imports.
from textual_astview import ASTView, ASTNode, NodeInfo, Source, __version__

##############################################################################
class MainDisplay( Screen ):
    """The main display of the app."""

    DEFAULT_CSS = """
    DirectoryTree {
        border: solid $primary-background-lighten-2;
        display: none;
    }

    DirectoryTree.visible {
        display: block;
    }

    DirectiryTree.initial {
        width: 100%;
    }

    DirectoryTree.insert {
        width: 20%;
    }

    DirectoryTree:focus-within {
        border: double $primary-lighten-2;
    }

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
        Binding( "ctrl+o", "open_new",       "Open" ),
        Binding( "ctrl+r", "toggle_rainbow", "Rainbow" ),
        Binding( "ctrl+d", "toggle_dark",    "Light/Dark" ),
        Binding( "ctrl+q", "app.quit",       "Quit" )
    ]
    """list[ Bindings ]: The bindings for the main screen."""

    UPDATE_DELAY: Final = 0.2
    """float: How long to leave it before updating the highlight in the source."""

    rainbow = reactive( False, init=False )
    """bool: Should 'rainbow' highlighting be used for the source?"""

    def __init__( self, cli_args: Namespace, *args: Any, **kwargs: Any ) -> None:
        """Initialise the main screen.

        Args:
            cli_args (Namespace): The command line arguments.
        """
        super().__init__( *args, **kwargs )
        self._args                       = cli_args
        self._refresh: Optional[ Timer ] = None

    def ast_pane( self ) -> ASTView:
        """Make an ASTView pane.

        Returns:
            ASTView: An ASTView pane for viewing the AST.
        """
        return ASTView( self._args.file )

    def source_pane( self ) -> Source:
        """Make a Source pane.

        Returns:
            Source: A source pane for viewing the code.
        """
        return Source(
            self._args.file,
            dark_theme  = self._args.dark_theme,
            light_theme = self._args.light_theme
        )

    def compose( self ) -> ComposeResult:
        """Compose the main app screen.

        Returns:
            ComposeResult: The result of composing the screen.
        """

        if self._args.file.is_file():
            body = [
                DirectoryTree( str( self._args.file.parent ), classes="insert" ), self.ast_pane(), self.source_pane()
            ]
        else:
            body = [ DirectoryTree( str( self._args.file ), classes="visible initial" ) ]

        yield Header()
        yield Vertical( Horizontal( *body ), NodeInfo() )
        yield Footer()

    def _init_tree( self ) -> None:
        """Set up the tree view when (re)loaded."""
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

    def on_mount( self ) -> None:
        """Sort the screen once the DOM is mounted."""
        if self.query( ASTView ):
            self._init_tree()
        else:
            self.query_one( DirectoryTree ).focus()

    def highlight_node( self, node: ASTNode ) -> None:
        """Update the display to highlight the given node.

        Args:
            node (ASTNode): The node to highlight.
        """
        self.query_one( NodeInfo ).show( node )
        self.query_one( Source ).highlight( node, self.rainbow )

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

    async def on_tree_node_selected( self, event: Tree.NodeSelected[ Any ] ) -> None:
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

    def watch_rainbow( self, new_value: bool ) -> None:
        """React to the rainbow flag being changed.

        Args:
            new_value (bool): The new value for the flag.
        """
        try:
            self.query_one( Source ).highlight(
                cast( ASTNode, self.query_one( ASTView ).cursor_node ), new_value
            )
        except NoMatches:
            pass

    def action_toggle_rainbow( self ) -> None:
        """Toggle the rainbow highlight flag."""
        self.rainbow = not self.rainbow

    def action_toggle_dark( self ) -> None:
        """Toggle daark mode."""
        self.app.dark = not self.app.dark
        try:
            self.query_one( Source ).dark = self.app.dark
            self.highlight_node( cast( ASTNode, self.query_one( ASTView ).cursor_node ) )
        except NoMatches:
            pass

    def action_open_new( self ) -> None:
        """Open a new file for viewing."""
        opener = self.query_one( DirectoryTree )
        opener.toggle_class( "visible" )
        if "visible" in opener.classes:
            opener.focus()

    async def on_directory_tree_file_selected( self, event: DirectoryTree.FileSelected ) -> None:
        """React to a file being selected in the directory tree.

        Args:
            event (DirectoryTree.FileSelected): The file selection event.
        """
        self._args.file = Path( event.path )
        if self.query( ASTView ):
            await self.query_one( ASTView ).remove()
            await self.mount( self.ast_pane(), before="Source" )
        else:
            await self.mount( self.ast_pane(), after="DirectoryTree" )
            await self.mount( self.source_pane(), after="ASTView" )
            self.query_one( DirectoryTree ).toggle_class( "initial", "insert" )
        self.query_one( Source ).show_file( self._args.file )
        self.query_one( DirectoryTree ).set_class( False, "visible" )
        self._init_tree()

### main.py ends here
