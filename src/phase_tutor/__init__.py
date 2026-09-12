"""相图导读：教学用二元 T–x 相图几何、解释器与中文读出。"""

from .diagrams.registry import all_diagrams, get_diagram, list_diagrams
from .figure import build_figure, figure_to_json
from .interpreter import interpret, walk_isopleth
from .readout import format_readout_text

__all__ = [
    "all_diagrams",
    "build_figure",
    "figure_to_json",
    "format_readout_text",
    "get_diagram",
    "interpret",
    "list_diagrams",
    "walk_isopleth",
]
