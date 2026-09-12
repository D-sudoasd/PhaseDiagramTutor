from __future__ import annotations

from ..models import Diagram
from . import cu_ni, fe_c, pb_sn, peritectic, ti_v

_ORDER = ("cu_ni", "pb_sn", "peritectic", "fe_c", "ti_v")
_BUILDERS = {
    "cu_ni": cu_ni.build,
    "pb_sn": pb_sn.build,
    "peritectic": peritectic.build,
    "fe_c": fe_c.build,
    "ti_v": ti_v.build,
}


def get_diagram(diagram_id: str) -> Diagram:
    try:
        return _BUILDERS[diagram_id]()
    except KeyError as exc:
        known = ", ".join(_ORDER)
        raise KeyError(f"未知相图 {diagram_id!r}。可选：{known}") from exc


def all_diagrams() -> list[Diagram]:
    return [get_diagram(i) for i in _ORDER]


def list_diagrams() -> list[tuple[str, str, str]]:
    return [(d.id, d.title_zh, d.subtitle_zh) for d in all_diagrams()]
