"""An AST viewer widget for Textual."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
import ast
from pathlib import Path
from functools import singledispatchmethod
from typing import Any, ClassVar, Optional, cast

##############################################################################
# Rich imports.
from rich.text import Text

##############################################################################
# Textual imports.
from textual import on
from textual.events import Mount
from textual.widgets import Tree
from textual.widgets.tree import TreeNode
from textual.binding import Binding

##############################################################################
ASTNode = TreeNode[Any]


##############################################################################
class ASTView(Tree[Any]):
    """The tree view of the AST."""

    # Note the hand-merged complement classes, keeping those of Tree.
    COMPONENT_CLASSES: ClassVar[set[str]] = Tree.COMPONENT_CLASSES | {
        "astview--def-name"
    }
    """Classes that can be used to style the AST view."""

    DEFAULT_CSS = """
    .astview--def-name {
        text-style: italic;
        color: #888;
    }
    """
    """The default CSS for the component."""

    BINDINGS = [
        Binding("ctrl+a", "toggle_all", "Toggle all"),
    ]
    """The bindings for the control."""

    def __init__(
        self, module: Path, *args: Any, name_defs: bool = True, **kwargs: Any
    ) -> None:
        """Initialise the view of the AST for the given module.

        Args:
            module: The path of the module to show.
            name_defs (optional): Include names in definition-type nodes?

        Note:
            By default function and class definition nodes will
            parenthetically show the name of the thing being defined. Use
            `name_defs` to turn this off.
        """

        # Remember some key stuff
        self._name_defs = name_defs
        self._module_path = module
        self._module: ast.Module | None = None

        if not module.is_dir():
            self._parse(module)

        # Now that we've configured things, get the Tree to do its own
        # thing.
        kwargs["label"] = module.name
        kwargs["data"] = self._module_path
        super().__init__(*args, **kwargs)

    @on(Mount)
    def _populate_tree(self) -> None:
        """Populate the tree with the module's AST."""
        if self._module is not None:
            self.add(self._module, self.root)
            self.select_node(self.root)

    def _parse(self, module: Path) -> None:
        """Parse the module.

        Args:
            module: The module to parse.
        """
        # Get the AST parsed in. I *suppose* it would make sense to try and
        # do this in an async way, perhaps? But for now anyway let's just
        # parse in the whole blasted thing up front. I've never found the
        # AST parser to be noticeably slow.
        try:
            self._module = ast.parse(module.read_text())
        except SyntaxError:
            self._module = None

    def reset(self, module: Path) -> None:
        """Reset the display to show a new module.

        Args:
            module: The new module to show.
        """
        if not module.is_dir():
            self._parse(module)
            super().reset(module.name, module)
            self._populate_tree()

    @property
    def module_path(self) -> Path:
        """Path: The path for the module being shown."""
        return self._module_path

    @singledispatchmethod
    def base_node(self, item: Any, to_node: ASTNode) -> ASTNode:
        """Attach a base node.

        Args:
            item: The item to associate with the node.
            to_node: The node to attach to.

        Returns:
            The new node.
        """
        return to_node.add(item.__class__.__name__, data=item)

    @base_node.register
    def _(self, item: ast.AST, to_node: ASTNode) -> ASTNode:
        """Attach a base node.

        Args:
            item: The item to associate with the node.
            to_node: The node to attach to.

        Returns:
            The new node.
        """
        # For most AST types the label will just be the class name.
        label = Text(item.__class__.__name__)

        # But, for some, let's include some extra detail too to help people
        # visually scan the display.
        if self._name_defs and isinstance(
            item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            (def_name := Text(f"({item.name})")).stylize(
                self.get_component_rich_style("astview--def-name", partial=True)
            )
            label = Text(f"{label} ") + def_name

        # Now go with what we've got.
        return to_node.add(label, data=item)

    @base_node.register
    def _(self, item: str, to_node: ASTNode) -> ASTNode:
        """Attach a base node.

        Args:
            item: The item to associate with the node.
            to_node: The node to attach to.

        Returns:
            The new node.
        """
        return to_node.add(item, data=item)

    @staticmethod
    def _items(item: Any) -> list[Any] | tuple[Any, ...]:
        """Cast an item to an item collection.

        Args:
            item: The item to cast to a collection.

        Returns:
            The item as a collection.

        Note:
            This is really a do-nothing method, it just helps cast things in
            a way that should be friendly to as many Pythons as possible.
        """
        return cast("list[ Any ] | tuple[ Any, ... ]", item)

    @classmethod
    def maybe_add(cls, value: Any) -> bool:
        """Does the value look like it should be added to the display?

        Args:
            value: The value to consider.

        Returns:
            `True` if the value should be added, `False` if not.
        """
        return bool(cls._items(value)) if isinstance(value, (list, tuple)) else True

    @singledispatchmethod
    def add(self, item: Any, to_node: ASTNode) -> None:
        """Add an entry to the tree.

        Args:
            itemThe ast entry to add.
            to_nodeThe node to add to.
        """
        # If we've been given a list or a tuple...
        if isinstance(item, (list, tuple)):
            # ...let's unroll what's inside, attaching everything to the
            # given node.
            for row in self._items(item):
                self.add(row, to_node)
        else:
            # Not a list or similar, so mark the item as a leaf and str it.
            to_node.add_leaf(repr(item), data=item)

    @add.register
    def _(self, item: ast.AST, to_node: ASTNode) -> None:
        """Add an AST item to the tree.

        Args:
            item: The ast entry to add.
            to_node: The node to add to.
        """

        # Create a new node to hand stuff off.
        node = self.base_node(item, to_node)

        # If the AST item has any fields...
        if item._fields:
            # ...add them all.
            for field in item._fields:
                if self.maybe_add(value := getattr(item, field)):
                    self.add(value, self.base_node(field, node))
        else:
            # It's a AST item with no fields, so don't allow expanding as
            # there's nothing to expand.
            node.allow_expand = False

    def action_toggle_all(self) -> None:
        """Toggle all the nodes from the selected node down."""
        if self.cursor_node is not None:
            self.cursor_node.toggle_all()


### astview.py ends here
