"""Provides a widget for displaying the source related to the AST view."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from pathlib import Path
from typing import Any, ClassVar, Final
from itertools import islice

##############################################################################
# Rich imports.
from rich.syntax import Syntax

##############################################################################
# Textual imports.
from textual import events
from textual.app import ComposeResult
from textual.widgets import Static
from textual.geometry import Region
from textual.reactive import reactive

##############################################################################
# Local imports.
from .astview import ASTNode
from .source_info import SourceInfo


##############################################################################
class Source(SourceInfo, can_focus=True):
    """Displays the source code for the file."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "source--ast-node-dark-mode-highlight",
        "source--ast-node-dark-mode-highlight-1",
        "source--ast-node-dark-mode-highlight-2",
        "source--ast-node-dark-mode-highlight-3",
        "source--ast-node-dark-mode-highlight-4",
        "source--ast-node-dark-mode-highlight-5",
        "source--ast-node-light-mode-highlight",
        "source--ast-node-light-mode-highlight-1",
        "source--ast-node-light-mode-highlight-2",
        "source--ast-node-light-mode-highlight-3",
        "source--ast-node-light-mode-highlight-4",
        "source--ast-node-light-mode-highlight-5",
    }
    """Classes that can be used to style the source view."""

    DEFAULT_CSS = """
    Source {
        height: 1fr;
        border: solid $primary-background-lighten-2;
        background: $panel;
        overflow: auto;
    }

    Source:focus {
        border: double $primary-lighten-2;
    }

    Source > Static {
        width: auto;
    }

    Source > .source--ast-node-dark-mode-highlight   { background: #700; text-style: bold italic; }
    Source > .source--ast-node-dark-mode-highlight-1 { background: #606; }
    Source > .source--ast-node-dark-mode-highlight-2 { background: #055; }
    Source > .source--ast-node-dark-mode-highlight-3 { background: #440; }
    Source > .source--ast-node-dark-mode-highlight-4 { background: #303; }
    Source > .source--ast-node-dark-mode-highlight-5 { background: #333; }

    Source > .source--ast-node-light-mode-highlight   { background: #F00; text-style: bold italic; }
    Source > .source--ast-node-light-mode-highlight-1 { background: #E0E; }
    Source > .source--ast-node-light-mode-highlight-2 { background: #0DD; }
    Source > .source--ast-node-light-mode-highlight-3 { background: #CC0; }
    Source > .source--ast-node-light-mode-highlight-4 { background: #B0B; }
    Source > .source--ast-node-light-mode-highlight-5 { background: #AAA; }
    """

    MAX_ANCESTOR: Final = 5
    """The maximum number of ancestors that can receive rainbow highlights."""

    DEFAULT_DARK_THEME: Final = "github-dark"
    """The default dark theme to use for the source."""

    DEFAULT_LIGHT_THEME: Final = "xcode"
    """The default light theme to use for the source."""

    dark = reactive(True)
    """Should the source be shown in a dark theme?"""

    def __init__(
        self,
        source: Path,
        *args: Any,
        dark_theme: str = DEFAULT_DARK_THEME,
        light_theme: str = DEFAULT_LIGHT_THEME,
        **kwargs: Any,
    ) -> None:
        """Initialise the source viewing widget.

        Args:
            dark_theme (optional): The theme to use for dark mode.
            light_theme (optional): The theme to use for light mode.
        """
        super().__init__(*args, **kwargs)
        self._source_file = source
        self._dark_theme = dark_theme
        self._light_theme = light_theme

    def _build_source(self) -> Syntax:
        """Builds a new `Stntax` of the file being viewed.

        Returns:
            The resulting `Syntax` instance.

        Note:
            This updates `_source`, but also returns is as a kindness.
        """
        if self._source_file.is_file():
            self._source = Syntax.from_path(
                str(self._source_file),
                line_numbers=True,
                lexer="python",
                theme=self._dark_theme if self.dark else self._light_theme,
            )
        else:
            self._source = Syntax(
                "",
                lexer="python",
                theme=self._dark_theme if self.dark else self._light_theme,
            )
        return self._source

    def _populate_source(self) -> None:
        """Repopulate the source display.

        Note:
            This should only be used when everything about the source has
            changed.
        """
        self.query_one(Static).update(self._build_source())

    def show_file(self, new_file: Path) -> None:
        """Show a new file in the widget.

        Args:
            new_file: The new file to show.
        """
        self._source_file = new_file
        self._populate_source()

    def compose(self) -> ComposeResult:
        """Compose the source display.

        Returns:
            The result of composing the source display.
        """
        yield Static()

    def on_mount(self) -> None:
        """Configure the widget after the DOM is up and going."""
        self._populate_source()

    def watch_dark(self, _: bool) -> None:
        """React to our own dark mode toggle.

        Note:
            This is only here while Textual's `watch` isn't behaving well.
        """
        self._populate_source()

    def on_click(self, _: events.Click) -> None:
        """React to a mouse click."""
        self.focus()

    @property
    def _highlight_style(self) -> str:
        return f"source--ast-node-{'dark' if self.dark else 'light'}-mode-highlight"

    def _highlight_ancestors(self, node: ASTNode) -> None:
        """Apply highlighting to location-based ancestors of the given node.

        Args:
            node: The node to find the ancestors of.
        """
        for rule, ancestor in reversed(
            list(
                enumerate(
                    islice(self.file_location_path_from(node), 1, self.MAX_ANCESTOR + 1)
                )
            )
        ):
            self._source.stylize_range(
                self.get_component_rich_style(
                    f"{self._highlight_style}-{rule + 1}", partial=True
                ),
                ancestor[:2],
                ancestor[2:],
            )

    def highlight(self, node: ASTNode, rainbow: bool = False) -> None:
        """Highlight the given AST data in the source.

        Args:
            node: The AST node to highlight.
            rainbow (optional): Use 'rainbow' highlighting?
        """

        # Sneaky nuking of any old styles. Rich's `Syntax` doesn't allow for
        # removing any stylized ranges so, other than nuking the while
        # Syntax and generating it again every time (slow!), the only option
        # we've got is to kill the list via an internal.
        #
        # pylint:disable=protected-access
        self._source._stylized_ranges = []

        # If rainbow highlighting is in effect, let's style the ancestors
        # first, so the current highlight is always at the top of the
        # styles.
        if rainbow:
            self._highlight_ancestors(node)

        # If the current node has a file location...
        if loc := self.file_location_of(node):
            # ...highlight and scroll to it.
            self._source.stylize_range(
                self.get_component_rich_style(self._highlight_style, partial=True),
                loc[:2],
                loc[2:],
            )
            line, _, end_line, _ = loc
            self.scroll_to_region(Region(y=line - 1, height=(end_line - line) + 1))

        # Update the display.
        self.query_one(Static).refresh()


### source.py ends here
