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
        width: 10fr;
    }

    ASTView:focus-within {
        border: double $primary-lighten-2;
    }

    Source {
        width: 10fr;
    }
    """

    BINDINGS = [
        Binding( "ctrl+left",  "shrink_left",    "", show=False ),
        Binding( "ctrl+right", "shrink_right",   "", show=False ),
        Binding( "ctrl+o",     "open_new",       "Open" ),
        Binding( "ctrl+r",     "toggle_rainbow", "Rainbow" ),
        Binding( "ctrl+d",     "toggle_dark",    "Light/Dark" ),
        Binding( "ctrl+q",     "app.quit",       "Quit" )
    ]
    """The bindings for the main screen."""

    UPDATE_DELAY: Final = 0.2
    """How long to leave it before updating the highlight in the source."""

    rainbow = reactive( False, init=False )
    """Should 'rainbow' highlighting be used for the source?"""

    ast_width: reactive[ int ] = reactive( 10, init=False )
    """The relative width of the reactive pane."""

    def __init__( self, cli_args: Namespace, *args: Any, **kwargs: Any ) -> None:
        """Initialise the main screen.

        Args:
            cli_args: The command line arguments.
        """
        super().__init__( *args, **kwargs )
        self._args                       = cli_args
        self._refresh: Optional[ Timer ] = None

    def ast_pane( self ) -> ASTView:
        """Make an ASTView pane.

        Returns:
            An ASTView pane for viewing the AST.
        """
        return ASTView( self._args.file, id="ast-view" )

    def source_pane( self ) -> Source:
        """Make a Source pane.

        Returns:
            A source pane for viewing the code.
        """
        return Source(
            self._args.file,
            dark_theme  = self._args.dark_theme,
            light_theme = self._args.light_theme
        )

    def compose( self ) -> ComposeResult:
        """Compose the main app screen.

        Returns:
            The result of composing the screen.
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
        if view.root.children:
            view.root.children[ 0 ].expand()
            if view.root.children[ 0 ].children:
                view.root.children[ 0 ].children[ 0 ].expand()
        view.focus()
        self.highlight_node( view.root )

    def on_mount( self ) -> None:
        """Sort the screen once the DOM is mounted."""
        if self.query( ASTView ):
            self._init_tree()
        else:
            self.query_one( DirectoryTree ).focus()

    def highlight_node( self, node: ASTNode ) -> None:
        """Update the display to highlight the given node.

        Args:
            node: The node to highlight.
        """
        self.query_one( NodeInfo ).show( node )
        self.query_one( Source ).highlight( node, self.rainbow )

    def on_tree_node_highlighted( self, event: Tree.NodeHighlighted ) -> None:
        """React to a node in the tree being highlighted.

        Args:
            event: The event to react to.
        """
        # Only handle highlight for the AST tree view. Note that for the
        # moment I have to dive into the private attributes of the node to
        # figure out which tree is sending the message.
        if event.node.tree.id != "ast-view":
            return
        # If there's a refresh pending...
        if self._refresh is not None:
            # ...stop it.
            self._refresh.stop()
        # Book in a fresh refresh the full delay on from this event.
        self._refresh = self.set_timer(
            self.UPDATE_DELAY, partial( self.highlight_node, event.node )
        )

    def on_tree_node_selected( self, event: Tree.NodeSelected ) -> None:
        """React to a node in the tree being selected.

        Args:
            event: The event to react to.
        """
        # Only handle selected for the AST tree view. Note that for the
        # moment I have to dive into the private attributes of the node to
        # figure out which tree is sending the message.
        if event.node.tree.id != "ast-view":
            return
        # If there's a refresh pending...
        if self._refresh is not None:
            # ...stop it and nuke all evidence of it.
            self._refresh.stop()
            self._refresh = None
        # Selected is a mouse click or someone bouncing on the enter key,
        # there's no point in delaying; so let's make it look a bit more
        # snappy by updating right away.
        self.highlight_node( event.node )

    def watch_rainbow( self, new_value: bool ) -> None:
        """React to the rainbow flag being changed.

        Args:
            new_value: The new value for the flag.
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

    def watch_ast_width( self ) -> None:
        """React to the AST view width being changed by the user."""
        self.query_one( ASTView ).styles.width = f"{self.ast_width}fr"
        self.query_one( Source ).styles.width = f"{10 + ( 10 - self.ast_width )}fr"

    def action_shrink_left( self ) -> None:
        """Shrink the left pane in the display."""
        if self.ast_width > 2:
            self.ast_width -= 1

    def action_shrink_right( self ) -> None:
        """Shrink the right pane in the display."""
        if self.ast_width < 18:
            self.ast_width += 1

    async def on_directory_tree_file_selected( self, event: DirectoryTree.FileSelected ) -> None:
        """React to a file being selected in the directory tree.

        Args:
            event: The file selection event.
        """
        self._args.file = Path( event.path )

        # Currently there's no good way to 100% empty out a Textual Tree and
        # populate it again from scratch. You can clear everything under the
        # root node, which would almost work, but then there's no public
        # method of setting a new label or data. Se we need to do a rebuild
        # dance instead. First, if there's already an ASTView in the DOM...
        if self.query( ASTView ):
            # ...remove it...
            await self.query_one( ASTView ).remove()
            # ...and then add a fresh one, splicing it into the display
            # before the source view.
            await self.mount( self.ast_pane(), before="Source" )
        else:
            # There's no ASTView. This means we've dome from just showing
            # just the directory tree and nothing else. In that case we need
            # to spin up and splice in an ASTView...
            await self.mount( self.ast_pane(), after="DirectoryTree" )
            # ...and then also a Source view.
            await self.mount( self.source_pane(), after="ASTView" )
            # Finally: the DirectiryTree will have been in its initial "fill
            # the display" state; so swap out that class and put it into
            # "insert me on the left when called upon" state.
            self.query_one( DirectoryTree ).toggle_class( "initial", "insert" )

        self.query_one( Source ).show_file( self._args.file )
        self.query_one( DirectoryTree ).set_class( False, "visible" )
        self._init_tree()

### main.py ends here
