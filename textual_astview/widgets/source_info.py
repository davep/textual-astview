"""A base class for widgets that show information about the source."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
import ast
from typing    import Iterator, Final
from pathlib   import Path
from itertools import groupby

##############################################################################
# Textual imports.
from textual.containers import Vertical

##############################################################################
# Local imports.
from .astview import ASTNode

##############################################################################
class SourceInfo( Vertical ):
    """Base class for information relating to showing source."""

    LOCATION_PROPS: Final = ( "lineno", "col_offset", "end_lineno", "end_col_offset" )
    """tuple[ str, ...]: The properties needed to highlight a location in the source."""

    @classmethod
    def has_location( cls, node: ASTNode ) -> bool:
        """Does the given node  have location information?

        Args:
            item (ASTNode): Am item from the AST.

        Returns:
            bool: `True` if the item has location information, otherwise `False.
        """
        return isinstance( node.data, ast.AST ) and all(
            hasattr( node.data, prop ) for prop in cls.LOCATION_PROPS
        )

    @classmethod
    def file_location_of( cls, node: ASTNode ) -> tuple[ int, int, int, int ] | None:
        """Find the file location of the given node.

        Args:
            node (ASTNode): The node in the tree to find the location of.

        Returns:
            tuple[ int, int, int, int ] | None: The location if one can be found.
        """
        if cls.has_location( node ):
            if ( item := node.data ) is not None: # Keep type checkers happy.
                return item.lineno, item.col_offset, item.end_lineno, item.end_col_offset
        elif node.parent is not None:
            return cls.file_location_of( node.parent )
        return None

    @classmethod
    def path_from( cls, node: ASTNode ) -> Iterator[ str ]:
        """Generate the path to the root from the given node.

        Args:
            node (ASTNode): The AST node to get the path from.

        Yields:
            str: The text for the node.
        """

        if isinstance( node.data, ast.AST ):
            yield node.data.__class__.__name__
        elif isinstance( node.data, Path ):
            yield node.data.name
        else:
            yield str( node.data )

        if node.parent is not None:
            yield from cls.path_from( node.parent )

    @classmethod
    def _file_location_path_from( cls, node: ASTNode ) -> Iterator[ tuple[ int, int, int, int ] ]:
        """Generate a file location path to the root from the given node.

        Args:
            node (ASTNode): The AST node to get the path from.

        Yields:
            tuple[ int, int, int, int ]: The file location.

        Note:
            This is a helper method for the non-internal of the same name.
        """

        # If this node has location data...
        if ( location := cls.file_location_of( node ) ) is not None:
            # ...make that available.
            yield location

        if node.parent is not None:
            yield from cls.file_location_path_from( node.parent )

    @classmethod
    def file_location_path_from( cls, node: ASTNode ) -> Iterator[ tuple[ int, int, int, int ] ]:
        """Generate a file location path to the root from the given node.

        Args:
            node (ASTNode): The AST node to get the path from.

        Yields:
            tuple[ int, int, int, int ]: The file location.
        """
        yield from ( pos for pos, _ in groupby( cls._file_location_path_from( node ) ) )

### source_info.py ends here
