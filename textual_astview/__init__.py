"""An AST viewing widget library plus app, built for and with Textual."""

######################################################################
# Main app information.
__author__     = "Dave Pearson"
__copyright__  = "Copyright 2022, Dave Pearson"
__credits__    = [ "Dave Pearson" ]
__maintainer__ = "Dave Pearson"
__email__      = "davep@davep.org"
__version__    = "0.1.0"
__licence__    = "MIT"

##############################################################################
# Import the widgets to make them easier to get at.
from .widgets.astview     import ASTView, ASTNode
from .widgets.node_info   import NodeInfo
from .widgets.source_info import SourceInfo
from .widgets.source      import Source

##############################################################################
# Export the widgets.
__all__ = [
    "ASTView",
    "ASTNode",
    "NodeInfo",
    "SourceInfo",
    "Source"
]

### __init__.py ends here
